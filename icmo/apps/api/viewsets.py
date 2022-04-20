from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class DeactivateModelMixin(mixins.DestroyModelMixin):
    """
    Deactivate instead of deleting a model instance.
    """

    def perform_destroy(self, instance):
        instance.deactivate(self.request.user)


class IcmoModelViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       DeactivateModelMixin,  # The override
                       mixins.ListModelMixin,
                       GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass