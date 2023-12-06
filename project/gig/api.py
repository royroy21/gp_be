from django.conf import settings
from django.http import Http404
from django.utils import timezone
from elasticsearch_dsl import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from project.core import permissions
from project.core.api import viewsets as core_viewsets
from project.core.search.queries import wildcard_query_for_words
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

    @action(detail=False, methods=["GET"])
    def search(self, request):
        search = GigDocument.search().query(Q("term", active=True))

        if not request.query_params.get("past_gigs"):
            start_date__gte = request.query_params.get("start_date__gte")
            search = search.filter(
                "range",
                **{"start_date": {"gte": start_date__gte or "now"}},
            )

        query = request.query_params.get("q", "")
        words = query.split(" ")

        username_queries = wildcard_query_for_words("user", words)
        title_queries = wildcard_query_for_words("title", words)
        description_queries = wildcard_query_for_words("description", words)
        location_queries = wildcard_query_for_words("location", words)
        country_queries = wildcard_query_for_words("country", words)
        genres_queries = wildcard_query_for_words("genres", words)
        combined_queries = (
            username_queries
            + title_queries
            + description_queries
            + location_queries
            + country_queries
            + genres_queries
        )
        # This bit looks odd. Basically this combines queries.
        combined_query = Q("bool", should=combined_queries)
        search = search.query(combined_query)

        if request.query_params.get("has_spare_ticket"):
            search = search.query(Q("term", has_spare_ticket=True))

        if request.query_params.get("has_replies"):
            search = search.query(Q("term", has_replies=True))

        # As `is_favorite` is a computed field determined at the time
        # of the API call we get favorite gigs from the requesting
        # user then perform a fresh elastic search query here.
        if request.query_params.get("is_favorite"):
            favorite_gigs_ids = request.user.favorite_gigs.filter(
                active=True,
            ).values_list("id", flat=True)
            favorite_gigs_query = Q(
                "terms", id__raw=[str(_id) for _id in favorite_gigs_ids]
            )
            search = search.query(favorite_gigs_query)

        my_gigs = request.query_params.get("my_gigs")
        if my_gigs:
            search = search.filter(
                "match",
                user=request.user.username,
            )

        return self.return_parsed_search_response(
            request,
            search,
            exclude_requesting_user=not my_gigs,
        )

    def return_parsed_search_response(
        self,
        request,
        search,
        exclude_requesting_user=False,
    ):
        """
        Takes an elasticsearch query then returns
        a serialized and paginated response.
        """
        # fmt: off
        search = search[0:settings.ELASTICSEARCH_PAGINATION_LIMIT]
        # fmt: on

        queryset = models.Gig.objects.filter(
            id__in=[record.id for record in search]
        ).order_by("start_date")
        if exclude_requesting_user:
            queryset = queryset.exclude(
                user__username=request.user.username,
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
