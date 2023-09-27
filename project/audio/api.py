from project.audio import models, serializers
from project.core import permissions
from project.core.api import viewsets as core_viewsets


class AlbumViewSet(core_viewsets.CustomModelViewSet):
    """
    Album API.
    """

    queryset = models.Album.objects.filter(active=True).order_by(
        "date_created",
    )
    serializer_class = serializers.AlbumSerializer

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

    def get_queryset(self):
        return self.queryset


class AudioViewSet(core_viewsets.CustomModelViewSet):
    """
    Audio API.
    """

    queryset = models.Audio.objects.filter(active=True).order_by(
        "date_created",
    )
    serializer_class = serializers.AudioSerializer

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

    def get_queryset(self):
        return self.queryset
