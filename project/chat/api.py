from django.db.models import Max
from rest_framework import exceptions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from project.chat import models, serializers
from project.core import permissions, search
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

        room_id = self.request.query_params.get("room_id")  # noqa
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
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
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

        queryset = self.queryset.filter(members=self.request.user)

        gig_id = self.request.query_params.get("gig_id")  # noqa
        if gig_id:
            # Return rooms for a gig
            return queryset.filter(gig__id=gig_id)

        return queryset

    def update(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        permissions.is_member(request, self.get_object())
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["GET"])
    def search(self, request):
        params = {}
        query = request.query_params.get("q", "")
        search.update_params_with_search_vectors(query, params)
        subquery = (
            models.Room.objects.filter(
                members=self.request.user,
                **params,
            )
            .distinct("id")
            .values_list("id", flat=True)
        )
        queryset = (
            models.Room.objects.filter(active=True, id__in=subquery)
            .annotate(last_message_date=Max("messages__date_created"))
            .order_by("-last_message_date")
            .exclude(messages__isnull=True)
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
    def rooms_with_unread_messages(self, request):
        """
        Returns rooms with unread messages.
        Sets unread messages to read.
        """
        user = request.user
        if not user.is_authenticated:
            raise exceptions.PermissionDenied

        room_ids = user.room_ids_with_unread_messages

        # Clearing rooms here as is assumed
        # messages have now been read client side.
        user.room_ids_with_unread_messages = []
        user.save()

        return Response({"rooms": room_ids})
