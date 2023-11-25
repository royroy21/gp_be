from django.http import Http404, HttpResponseBadRequest
from django.utils import timezone
from django_elasticsearch_dsl_drf import constants, filter_backends
from django_elasticsearch_dsl_drf import viewsets as dsl_drf_view_sets
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination
from elasticsearch_dsl import Q
from rest_framework import status
from rest_framework.response import Response

from project.core import permissions
from project.core.api import mixins as core_mixins
from project.core.api import viewsets as core_viewsets
from project.gig import models, serializers
from project.gig.search_indexes.documents.gig import GigDocument


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
            return self.queryset.exclude(start_date__lte=timezone.now())

        my_gigs = self.request.query_params.get("my_gigs")
        if my_gigs:
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


class GigDocumentViewSet(
    core_mixins.ListModelMixinWithSerializerContext,
    dsl_drf_view_sets.BaseDocumentViewSet,
):
    """
    Read only Gig API.

    This API uses elastic search.

    An example URL query could be:
    search/gig/?search=doo

    An example URL query using filtering on start_date and has_spare_ticket:
    search/gig/?search=doom&start_date__gt=2023-05-01&has_spare_ticket=true

    An example URL query using order_by
    search/gig/?search=doom&start_date__gt=2023-05-01&order_by_start_date
    """

    document = GigDocument
    serializer_class = serializers.GigDocumentSerializer
    pagination_class = PageNumberPagination
    lookup_field = "id"
    filter_backends = [
        filter_backends.FilteringFilterBackend,
        filter_backends.OrderingFilterBackend,
        filter_backends.CompoundSearchFilterBackend,
    ]
    search_fields = (
        "user",
        "title",
        "location",
        "country",
        "description",
        "genres",
    )
    filter_fields = {
        "title": "title.raw",
        "location": "location.raw",
        "has_spare_ticket": {
            "field": "has_spare_ticket",
            "lookups": [
                constants.TRUE_VALUES,
            ],
        },
        "has_replies": {
            "field": "has_replies",
            "lookups": [
                constants.TRUE_VALUES,
            ],
        },
        "start_date": {
            "field": "start_date",
            "lookups": [
                constants.LOOKUP_FILTER_RANGE,
                constants.LOOKUP_QUERY_IN,
                constants.LOOKUP_QUERY_GT,
                constants.LOOKUP_QUERY_GTE,
            ],
        },
    }
    ordering_fields = {
        "start_date": "start_date",
        "title": "title.raw",
        "location": "location.raw",
    }
    ordering = (
        "start_date",
        "title",
        "location",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.exclude("match", active=False)
        if not self.request.user.is_authenticated:
            return queryset.filter("range", **{"start_date": {"gte": "now"}})

        # As `is_favorite` is a computed field determined at the time
        # of the API call we get favorite gigs from the requesting
        # user then perform a fresh elastic search query here.
        if self.request.query_params.get("is_favorite"):  # noqa
            favorite_gigs_ids = self.request.user.favorite_gigs.filter(  # noqa
                active=True,
            ).values_list("id", flat=True)
            favorite_gigs_query = Q(
                "terms", id__raw=[str(_id) for _id in favorite_gigs_ids]
            )
            return queryset.query(favorite_gigs_query).sort("start_date")

        my_gigs = self.request.query_params.get("my_gigs")
        if my_gigs:
            past_gigs = self.request.query_params.get("past_gigs")
            queryset = queryset.filter(
                "match",
                user=self.request.user.username,
            )
            if past_gigs:
                return queryset.sort("start_date")
            else:
                return queryset.filter(
                    "range",
                    **{"start_date": {"gte": "now"}},
                ).sort("start_date")

        queryset = queryset.exclude("match", user=self.request.user.username)
        return queryset.filter("range", **{"start_date": {"gte": "now"}}).sort(
            "start_date"
        )

    def retrieve(self, request, *args, **kwargs):
        return HttpResponseBadRequest(
            "The API route should be used for detail views.",
        )
