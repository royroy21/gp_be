from django.utils import timezone
from rest_framework import viewsets

from project.core import permissions
from project.gig import models, serializers


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
        my_gigs = self.request.query_params.get("my_gigs")
        if my_gigs:
            return models.Gig.objects.filter(
                user=self.request.user,
                active=True,
            )
        return (
            models.Gig.objects.filter(active=True)
            .exclude(user=self.request.user)
            .exclude(start_date__lte=timezone.now())
        )
