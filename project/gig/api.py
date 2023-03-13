from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django_elasticsearch_dsl_drf import constants, filter_backends
from django_elasticsearch_dsl_drf import viewsets as dsl_drf_viewsets
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination
from rest_framework import viewsets

from project.core import permissions
from project.gig import models, serializers
from project.gig.search_indexes.documents.gig import GigDocument


class GigViewSet(viewsets.ModelViewSet):
    """
    Gig API. List and retrieve are left open in regards to permissions.
    """

    queryset = models.Gig.objects.filter(active=True).order_by("start_date")
    serializer_class = serializers.GigSerializer

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
        permissions.is_owner(request, self.get_object())
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.exclude(start_date__lte=timezone.now())

        my_gigs = self.request.query_params.get("my_gigs")
        if my_gigs:
            # Return all gigs even those out of date.
            return self.queryset.filter(user=self.request.user)

        # User should be able to get any gig if lookup_field (pk) is provided.
        if (
            self.request.method in ["GET", "PUT", "PATCH"]
            and self.lookup_field in self.kwargs.keys()
        ):
            return self.queryset

        return self.queryset.exclude(user=self.request.user).exclude(
            start_date__lte=timezone.now()
        )


class GigDocumentViewSet(dsl_drf_viewsets.BaseDocumentViewSet):
    """
    Read only Gig API.

    This API uses elastic search.

    An example URL query could be:
    search/gig/?search=doo

    An example URL query with filtering on start_date and has_spare_ticket:
    search/gig/?search=doom&start_date__gt=2023-05-01&has_spare_ticket=true

    An example URL query with order_by
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
    search_fields = {
        "user": {"fuzziness": "AUTO"},
        "title": {"fuzziness": "AUTO"},
        "location": {"fuzziness": "AUTO"},
        "country": {"fuzziness": "AUTO"},
        "description": {"fuzziness": "AUTO"},
        "genres": {"fuzziness": "AUTO"},
    }
    filter_fields = {
        "title": "title.raw",
        "location": "location.raw",
        "has_spare_ticket": {
            "field": "has_spare_ticket",
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
        if not self.request.user.is_authenticated:
            return queryset.filter("range", **{"start_date": {"gte": "now"}})

        my_gigs = self.request.query_params.get("my_gigs")
        if my_gigs:
            # Return all gigs even those out of date.
            return queryset.filter("match", user=self.request.user.username)

        queryset = queryset.exclude("match", user=self.request.user.username)
        return queryset.filter("range", **{"start_date": {"gte": "now"}})

    def retrieve(self, request, *args, **kwargs):
        return HttpResponseBadRequest(
            "The API route should be used for detail views.",
        )


@require_http_methods(["GET"])
def suggest_genre(request):
    """
    Suggest Genre.

    The URL is made to match the URL used by django_elasticsearch_dsl's
    suggester so this view can be easily converted to use suggester in
    the future.

    An example URL query could be:
    search/genre/suggest/?genre_suggest__completion=ind
    """
    # TODO - convert to Elastic search suggester
    suggest = request.GET.get("genre_suggest__completion")
    query = Q(Q(genre__startswith=suggest) | Q(genre__icontains=suggest))
    result = models.Genre.objects.filter(query).order_by("rank")[:50]
    return JsonResponse(
        serializers.GenreSerializer(result, many=True).data,
        safe=False,
    )
