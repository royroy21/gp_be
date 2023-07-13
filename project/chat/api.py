from rest_framework import exceptions, mixins
from rest_framework.viewsets import GenericViewSet

from project.chat import models, serializers


class MessageViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    Returns messages for a Room.
    """

    queryset = models.Message.objects.filter(active=True).order_by(
        "date_created",
    )
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        # if not self.request.user.is_authenticated:
        #     return self.queryset.none()

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


class RoomViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    Returns active Rooms for a user.
    """

    queryset = (
        models.Room.objects.filter(active=True)
        .order_by("-date_created")
        .exclude(messages__isnull=True)
    )
    serializer_class = serializers.RoomSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()

        return self.queryset.filter(members=self.request.user)
