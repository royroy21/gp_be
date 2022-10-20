from django.contrib.auth import get_user_model
from rest_framework import generics, mixins
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from project.core import permissions
from project.custom_user import serializers

User = get_user_model()


class UserDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericAPIView,
):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    serializer_class_if_not_owner = serializers.UserSerializerIfNotOwner

    def get_serializer_if_not_owner_class(self, *args, **kwargs):
        serializer_class = self.serializer_class_if_not_owner
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id != request.user.id:
            # Using this serializer so that emails are hidden.
            serializer = self.get_serializer_if_not_owner_class(instance)
        else:
            serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        permissions.is_authenticated(request)
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        permissions.is_owner(request, self.get_object())
        return self.partial_update(request, *args, **kwargs)


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def list(self, request, *args, **kwargs):
        permissions.is_authenticated(request)
        queryset = self.get_queryset()
        # Using this serializer so that emails are hidden.
        serializer = serializers.UserSerializerIfNotOwner(queryset, many=True)
        return Response(serializer.data)
