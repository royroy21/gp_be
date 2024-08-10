import json

from django import forms, http
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from project.core import permissions
from project.core.drf import blacklist
from project.custom_email import send_reset_password_email
from project.custom_user import models, serializers
from project.gig import models as gig_models

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True).order_by("username")
    serializer_class = serializers.UserSerializer
    serializer_class_if_not_owner = serializers.UserSerializerIfNotOwner

    def create(self, request, *args, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())
        serializer = serializers.CreateUserSerializer(
            data=request.data,
            *args,
            **kwargs,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def get_serializer(self, instance=None, *args, **kwargs):
        # If no instance, instance is being created.
        if self.request.user == instance:
            return super().get_serializer(instance, *args, **kwargs)
        # Using this serializer so emails are hidden.
        return self.get_serializer_if_not_owner(instance, *args, **kwargs)

    def get_serializer_if_not_owner(self, *args, **kwargs):
        serializer_class = self.serializer_class_if_not_owner
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        if (
            self.request.user.is_authenticated
            and self.request.method == "GET"
            and self.lookup_field not in self.kwargs.keys()
        ):
            return self.queryset.exclude(id=self.request.user.id)
        return self.queryset

    @action(detail=False, methods=["GET"])
    def search(self, request):
        params = {
            "is_active": True,
        }
        if request.query_params.get("has_active_gigs"):
            params.update(
                {
                    "gigs__active": True,
                    "gigs__start_date__gte": timezone.now(),
                }
            )
        if request.query_params.get("is_favorite"):
            favorite_users_ids = request.user.favorite_users.all().values_list(
                "id",
                flat=True,
            )
            params.update({"id__in": favorite_users_ids})

        query = request.query_params.get("q")
        if query:
            cleaned_query = " ".join(
                word
                for word in query.split(" ")
                if word.lower() not in settings.ENGLISH_STOP_WORDS
            )
            params.update({"search_vector": cleaned_query})

        subquery = (
            User.objects.filter(**params)
            .distinct("id")
            .values_list("id", flat=True)
        )
        queryset = (
            User.objects.filter(id__in=subquery)
            .order_by("id")
            .exclude(username=request.user.username)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serialized = self.get_serializer(
            queryset,
            many=True,
        )
        return Response(serialized.data)

    @action(detail=False, methods=["GET"])
    def me(self, request):
        permissions.is_authenticated(request)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(url_path="notification-token", detail=False, methods=["POST"])
    def notification_token(self, request):
        """
        Mobile apps post their token for use with push notifications here.
        """
        permissions.is_authenticated(request)
        token = request.data.get("token")
        active = request.data.get("active")
        if not token or active is None:
            raise exceptions.ParseError

        query = models.NotificationToken.objects.filter(
            token=token,
            user=request.user,
        )
        existing_token = query.first()
        if existing_token:
            if existing_token.active != active:
                existing_token.active = active
                existing_token.save()
        else:
            models.NotificationToken.objects.create(
                token=token,
                user=request.user,
                active=active,
            )
        return Response({"operation": "success"})

    @action(url_path="add-favorite-user", detail=False, methods=["POST"])
    def add_favorite_user(self, request):
        user = self.get_favorite_user(request)
        request.user.favorite_users.add(user)
        request.user.save()
        return Response({"operation": "success"})

    @action(url_path="remove-favorite-user", detail=False, methods=["POST"])
    def remove_favorite_user(self, request):
        user = self.get_favorite_user(request)
        request.user.favorite_users.remove(user)
        request.user.save()
        return Response({"operation": "success"})

    def get_favorite_user(self, request):  # noqa
        """
        Performs checks and returns user for favorite user operations.
        """
        permissions.is_authenticated(request)
        user_id = request.data.get("id")
        if not user_id:
            raise exceptions.ParseError

        user = models.User.objects.filter(id=user_id).first()
        if not user:
            raise exceptions.NotFound

        return user

    @action(url_path="add-favorite-gig", detail=False, methods=["POST"])
    def add_favorite_gig(self, request):
        gig = self.get_favorite_gig(request)
        request.user.favorite_gigs.add(gig)
        request.user.save()
        return Response({"operation": "success"})

    @action(url_path="remove-favorite-gig", detail=False, methods=["POST"])
    def remove_favorite_gig(self, request):
        gig = self.get_favorite_gig(request)
        request.user.favorite_gigs.remove(gig)
        request.user.save()
        return Response({"operation": "success"})

    def get_favorite_gig(self, request):  # noqa
        """
        Performs checks and returns gig for favorite gig operations.
        """
        permissions.is_authenticated(request)
        gig_id = request.data.get("id")
        if not gig_id:
            raise exceptions.ParseError

        gig = gig_models.Gig.objects.filter(id=gig_id).first()
        if not gig:
            raise exceptions.NotFound

        return gig


class EmailForm(forms.Form):
    email = forms.EmailField()


@csrf_exempt
@require_http_methods(["POST"])
def reset_password_request(request):
    form = EmailForm(json.loads(request.body))
    if not form.is_valid():
        return http.JsonResponse(
            {"detail": "Email is not valid."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = form.cleaned_data["email"]
    user = User.objects.filter(email=email).first()
    if not user:
        return http.JsonResponse(
            {"detail": "No user with that email address exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    reset_password_token = models.ResetPasswordToken.objects.create(user=user)
    send_reset_password_email(
        to_address=email,
        token=reset_password_token.token,
    )
    return http.JsonResponse({"message": "Reset password password sent."})


class ResetPasswordForm(forms.Form):
    password = forms.CharField()
    token = forms.CharField()


@csrf_exempt
@require_http_methods(["POST"])
def reset_password(request):
    form = ResetPasswordForm(json.loads(request.body))
    if not form.is_valid():
        return http.JsonResponse(
            {"detail": "Malformed data."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = form.cleaned_data["token"]
    token = models.ResetPasswordToken.objects.filter(
        token=token, active=True
    ).first()
    if not token:
        return http.JsonResponse(
            {"detail": "No active reset password token found."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    new_password = form.cleaned_data["password"]
    user = token.user
    user.set_password(new_password)
    user.save()
    token.active = False
    token.save()
    blacklist.blacklist_user_tokens(user)

    return http.JsonResponse({"message": "Password reset"})
