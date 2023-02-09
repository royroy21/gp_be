from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django_elasticsearch_dsl_drf import filter_backends
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

    queryset = models.Gig.objects.filter(active=True)
    serializer_class = serializers.GigSerializer

    def create(self, request, *args, **kwargs):
        permissions.is_authenticated(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        return super().update(request, *args, **kwargs)

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
            return self.queryset.filter(user=self.request.user, active=True)

        return (
            self.queryset.filter(active=True)
            .exclude(user=self.request.user)
            .exclude(start_date__lte=timezone.now())
        )


class GigDocumentViewSet(dsl_drf_viewsets.DocumentViewSet):
    """
    Read only Gig API.

    This API uses elastic search.

    As example URL query could be:
    http://localhost:8000/search/gig/?search=doo
    """

    document = GigDocument
    serializer_class = serializers.GigDocumentSerializer
    pagination_class = PageNumberPagination
    lookup_field = "id"
    filter_backends = [
        filter_backends.CompoundSearchFilterBackend,
    ]
    search_fields = {
        "user": {"fuzziness": "AUTO"},
        "title": {"fuzziness": "AUTO"},
        "venue": {"fuzziness": "AUTO"},
        "location": {"fuzziness": "AUTO"},
        "description": {"fuzziness": "AUTO"},
        "genre": {"fuzziness": "AUTO"},
    }
    ordering = (
        "location",
        "title",
        "venue",
        "genre",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter("range", **{"start_date": {"gte": "now"}})

        if not self.request.user.is_authenticated:
            return queryset.exclude("match", user=self.request.user.username)

        return queryset


@require_http_methods(["GET"])
def suggest_genre(request):
    """
    Suggest Genre.

    The URL is made to match the URL used by django_elasticsearch_dsl's
    suggester so this view can be easily converted to use suggester in
    the future.

    As example URL query could be:
    http://localhost:8000/search/genre/suggest/?genre_suggest__completion=ind
    """
    # TODO - convert to Elastic search suggester
    suggest = request.GET.get("genre_suggest__completion")
    query = Q(Q(genre__startswith=suggest) | Q(genre__icontains=suggest))
    result = models.Genre.objects.filter(query).order_by("rank")[:50]
    return JsonResponse(
        serializers.GenreSerializer(result, many=True).data,
        safe=False,
    )
