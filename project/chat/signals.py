from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from project.chat import models, serializers
from project.core.requests import SudoRequest
from project.custom_user import tasks as user_tasks


@receiver(post_save, sender=models.Message)
def create_chat_message(sender, instance, created, **kwargs):
    if not created or not settings.PUSH_NOTIFICATIONS_ENABLED:
        return

    # Send push notification to other members of the room.
    for user in instance.room.members.exclude(id=instance.user.id):
        request = SudoRequest(user=user)
        room_serialized = serializers.RoomSerializer(
            instance.room,
            context={"request": request},
        )
        user_tasks.send_push_notification.delay(
            user_id=user.id,
            title=f"Message from {instance.user.username}",
            message=instance.message,
            data={"type": "room", "serialized_object": room_serialized.data},
        )
