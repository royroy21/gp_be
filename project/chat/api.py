from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from project.chat import models, serializers


class MessageViewSet(GenericViewSet):
    queryset = models.Message.objects.filter(active=True).order_by(
        "date_created"
    )
    serializer_class = serializers.MessageSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

        return self.queryset.filter(room=room)
