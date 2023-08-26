from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest
from django_elasticsearch_dsl_drf import filter_backends
from django_elasticsearch_dsl_drf import viewsets as dsl_drf_view_sets
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from project.core import permissions
from project.core.api import mixins as core_mixins
from project.custom_user import models, serializers
from project.custom_user.search_indexes.documents.user import UserDocument

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("date_joined")
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

    def retrieve(self, request, *args, **kwargs):
        permissions.is_authenticated(request)
        return super().retrieve(request, *args, **kwargs)

    def get_serializer(self, instance=None, *args, **kwargs):
        # If no instance, instance is being created.
        if instance is None:
            return super().get_serializer(instance, *args, **kwargs)
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

    def get_queryset(self):
        if (
            self.request.user.is_authenticated
            and self.request.method == "GET"
            and self.lookup_field not in self.kwargs.keys()
        ):
            return self.queryset.exclude(id=self.request.user.id)
        return self.queryset

    def list(self, request, *args, **kwargs):
        permissions.is_authenticated(request)
        return super().list(request, *args, **kwargs)

    def destroy(self, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
            return Response(
                {"error": ["Malformed POST data."]},
                status=400,
            )
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


class UserDocumentViewSet(
    core_mixins.ListModelMixinWithSerializerContext,
    dsl_drf_view_sets.BaseDocumentViewSet,
):
    """
    Read only User API.

    This API uses elastic search.

    An example URL query could be:
    search/user/?search=fred
    """

    document = UserDocument
    serializer_class = serializers.UserDocumentSerializer
    pagination_class = PageNumberPagination
    lookup_field = "id"
    filter_backends = [
        filter_backends.FilteringFilterBackend,
        filter_backends.OrderingFilterBackend,
        filter_backends.CompoundSearchFilterBackend,
    ]
    search_fields = (
        "username",
        "country",
        "bio",
        "genres",
    )
    filter_fields = {
        "username": "username.raw",
        "country": "country.raw",
    }
    ordering_fields = {
        "username": "username",
    }
    ordering = ("username",)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude("match", user=self.request.user.username)

    def retrieve(self, request, *args, **kwargs):
        return HttpResponseBadRequest(
            "The API route should be used for detail views.",
        )
