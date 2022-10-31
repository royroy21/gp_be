from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from project.core import permissions
from project.custom_user import serializers

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    serializer_class_if_not_owner = serializers.UserSerializerIfNotOwner

    def retrieve(self, request, *args, **kwargs):
        permissions.is_authenticated(request)
        return super().retrieve(request, *args, **kwargs)

    def get_serializer(self, instance=None, *args, **kwargs):
        # If no instance this means instance is being created.
        if instance is None:
            return super().get_serializer(instance, *args, **kwargs)
        if self.request.user == instance:
            return super().get_serializer(instance, *args, **kwargs)
        # Using this serializer so that emails are hidden.
        return self.get_serializer_if_not_owner(instance, *args, **kwargs)

    def get_serializer_if_not_owner(self, *args, **kwargs):
        serializer_class = self.serializer_class_if_not_owner
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        permissions.is_authenticated(request)
        queryset = self.get_queryset()
        # Using this serializer so that emails are hidden.
        serializer = serializers.UserSerializerIfNotOwner(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def me(self, request):
        permissions.is_authenticated(request)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
