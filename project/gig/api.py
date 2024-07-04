from django.conf import settings
from django.http import Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from project.core import permissions
from project.core.api import viewsets as core_viewsets
from project.gig import models, serializers


class GigViewSet(core_viewsets.CustomModelViewSet):
    """
    Gig API. List and retrieve are left open in regards to permissions.
    """

    queryset = models.Gig.objects.filter(active=True).order_by("start_date")
    serializer_class = serializers.GigSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a Gig.

        An inactive Gig can be returned.

        One example when this is useful is when a
        Gig room navigates to an inactive Gig.
        """
        try:
            instance = models.Gig.objects.get(id=kwargs["pk"])
        except (models.Gig.DoesNotExist, KeyError):
            raise Http404("Gig does not exist.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        permissions.is_authenticated(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Sets Gig to inactive.
        """
        # Getting instance like this so a user can always delete
        # regardless of what's happening in get_queryset().
        try:
            instance = models.Gig.objects.get(id=kwargs["pk"])
        except (models.Gig.DoesNotExist, KeyError):
            raise Http404("Gig does not exist.")
        permissions.is_owner(request, instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            user_id = self.request.query_params.get("user_id")  # noqa
            if user_id:
                return self.queryset.filter(user__id=user_id).exclude(
                    start_date__lte=timezone.now(),
                )
            return self.queryset.exclude(start_date__lte=timezone.now())

        user_id = self.request.query_params.get("user_id")  # noqa
        if user_id:
            return self.queryset.filter(user__id=user_id).exclude(
                start_date__lte=timezone.now(),
            )

        if self.request.query_params.get("my_gigs"):  # noqa
            return self.queryset.filter(user=self.request.user).exclude(
                start_date__lte=timezone.now(),
            )

        # User should be able to get any gig if lookup_field (pk) is provided.
        if (
            self.request.method in ["GET", "PUT", "PATCH"]
            and self.lookup_field in self.kwargs.keys()
        ):
            return self.queryset

        return self.queryset.exclude(user=self.request.user).exclude(
            start_date__lte=timezone.now()
        )

    @action(detail=False, methods=["GET"])
    def search(self, request):
        params = {
            "active": True,
        }
        if not request.query_params.get("past_gigs"):
            start_date__gte = request.query_params.get("start_date__gte")
            params.update(
                {"start_date__gte": start_date__gte or timezone.now()}
            )

        if request.query_params.get("has_spare_ticket"):
            params.update({"has_spare_ticket": True})

        if request.query_params.get("has_replies"):
            params.update(
                {
                    "rooms__active": True,
                    "rooms__messages__isnull": False,
                }
            )

        if request.query_params.get("is_favorite"):
            favorite_gigs_ids = request.user.favorite_gigs.filter(
                active=True,
            ).values_list("id", flat=True)
            params.update({"id__in": favorite_gigs_ids})

        my_gigs = request.query_params.get("my_gigs")
        if my_gigs:
            params.update({"user": request.user})

        query = request.query_params.get("q")
        if query:
            cleaned_query = " ".join(
                word
                for word in query.split(" ")
                if word.lower() not in settings.ENGLISH_STOP_WORDS
            )
            params.update(
                {
                    "search_vector": cleaned_query,
                }
            )

        subquery = (
            models.Gig.objects.filter(**params)
            .distinct("id")
            .values_list("id", flat=True)
        )
        queryset = models.Gig.objects.filter(id__in=subquery).order_by(
            "start_date"
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
