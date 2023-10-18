from rest_framework import status
from rest_framework.response import Response

from project.audio import models, serializers
from project.core import permissions
from project.core.api import viewsets as core_viewsets


class AlbumViewSet(core_viewsets.CustomModelViewSet):
    """
    Album API. List and retrieve are left open in regard to permissions.
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
        instance = self.get_object()
        if instance.is_default:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": ["Cannot delete the default album."]},
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        profile_id = self.request.query_params.get("profile_id")  # noqa
        if profile_id:
            return self.queryset.filter(profile__id=profile_id)
        gig_id = self.request.query_params.get("gig_id")  # noqa
        if gig_id:
            return self.queryset.filter(gig_id__id=gig_id)

        return self.queryset


class AudioViewSet(core_viewsets.CustomModelViewSet):
    """
    Audio API. List and retrieve are left open in regard to permissions.
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
        audio = self.get_object()
        self.perform_destroy(audio)
        serializers.AudioSerializer.reinitialize_track_positions(audio.album)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return self.queryset
