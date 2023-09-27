from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from project.core.api import mixins as core_mixins


class CustomModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    core_mixins.CustomDestroyModelMixin,
    core_mixins.ListModelMixinWithSerializerContext,
    GenericViewSet,
):
    """
    The same as DRF's ModelViewSet only with
    replaced DestroyModelMixin and ListModelMixin.
    """

    pass
