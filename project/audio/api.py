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
        gig_id = self.request.query_params.get("gig__id")  # noqa
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
        """
        Overwriting here so to inject album.
        Unable to do at serializer due to circular imports.
        """
        permissions.is_authenticated(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data["album"] = self.get_serialized_album(data["album"])
        return Response(
            data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        """
        Overwriting here so to inject album.
        Unable to do at serializer due to circular imports.
        """
        permissions.is_owner(request, self.get_object())

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        data = serializer.data
        data["album"] = self.get_serialized_album(data["album"])
        return Response(data)

    def get_serialized_album(self, album):
        if not album:
            return None
        return serializers.AlbumSerializer(
            instance=models.Album.objects.get(id=album),
            context=self.get_serializer_context(),
        ).data

    def partial_update(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset
