from rest_framework import mixins
from rest_framework.response import Response


class CustomDestroyModelMixin(mixins.DestroyModelMixin):
    """
    Sets active to False instead of performing full delete.
    """

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()


class ListModelMixinWithSerializerContext:
    """
    List a queryset.

    Passes serializer_context to the serializer so that
    it has access to the request object.
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())  # noqa

        page = self.paginate_queryset(queryset)  # noqa
        if page is not None:
            serializer = self.get_serializer(  # noqa
                page,
                many=True,
                context=self.get_serializer_context(),  # noqa
            )
            return self.get_paginated_response(serializer.data)  # noqa

        serializer = self.get_serializer(queryset, many=True)  # noqa
        return Response(serializer.data)
