from django.db.models import Max
from django.http import HttpResponseBadRequest
from django_elasticsearch_dsl_drf import filter_backends
from django_elasticsearch_dsl_drf import viewsets as dsl_drf_view_sets
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination
from rest_framework import exceptions, mixins
from rest_framework.viewsets import GenericViewSet

from project.chat import models, serializers
from project.chat.search_indexes.documents.room import RoomDocument
from project.core.api import mixins as core_mixins


class MessageViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    Returns messages for a Room.
    """

    queryset = models.Message.objects.filter(active=True).order_by(
        "date_created",
    )
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()

        room_id = self.request.query_params.get("room_id")
        if not room_id:
            raise exceptions.PermissionDenied

        room_query = models.Room.objects.filter(id=room_id)
        if not room_query.exists():
            raise exceptions.PermissionDenied

        room = room_query.first()
        if self.request.user not in room.members.filter(is_active=True):
            raise exceptions.PermissionDenied

        return self.queryset.filter(room=room).reverse()


class RoomViewSet(
    core_mixins.ListModelMixinWithSerializerContext,
    GenericViewSet,
):
    """
    Returns active Rooms for a user.
    """

    queryset = (
        models.Room.objects.filter(active=True)
        .annotate(last_message_date=Max("messages__date_created"))
        .order_by("-last_message_date")
        .exclude(messages__isnull=True)
    )
    serializer_class = serializers.RoomSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()

        return self.queryset.filter(members=self.request.user)


class RoomDocumentViewSet(
    core_mixins.ListModelMixinWithSerializerContext,
    dsl_drf_view_sets.BaseDocumentViewSet,
):
    """
    Read only Room API.

    This API uses elastic search.

    An example URL query could be:
    search/room/?search=fred
    """

    document = RoomDocument
    serializer_class = serializers.RoomDocumentSerializer
    pagination_class = PageNumberPagination
    lookup_field = "id"
    filter_backends = [
        filter_backends.FilteringFilterBackend,
        filter_backends.OrderingFilterBackend,
        filter_backends.CompoundSearchFilterBackend,
    ]
    search_fields = (
        "members",
        "gig",
    )
    filter_fields = {
        "members": "members.raw",
        "gig": "gig.raw",
    }
    ordering_fields = {
        "last_message_date": "last_message_date",
    }

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter("match", members=self.request.user.username)
            .filter("match", has_messages=True)
            .sort("-last_message_date")
        )

    def retrieve(self, request, *args, **kwargs):
        return HttpResponseBadRequest(
            "The API route should be used for detail views.",
        )
