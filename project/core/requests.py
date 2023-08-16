from project.site import domain


class SudoRequest:
    """
    Used for injecting request object into
    serializer when request is not available.

    example:
        request = SudoRequest(user=user)
        room_serialized = serializers.RoomSerializer(
            instance.room,
            context={"request": request},
        )
    """

    def __init__(self, user):
        self.user = user

    def build_absolute_uri(self, relative_uri):  # noqa
        return domain.build_absolute_uri(relative_uri)
