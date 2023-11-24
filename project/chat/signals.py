from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from project.chat import models, serializers
from project.chat.search_indexes.update.room import update_room_search_index
from project.core.requests import SudoRequest
from project.custom_user import tasks as user_tasks
from project.gig.search_indexes.update import gig as gig_search_indexes


@receiver(post_save, sender=models.Message)
def create_chat_message(sender, instance, created, **kwargs):
    update_room_search_index(instance.room)

    if not created or not settings.PUSH_NOTIFICATIONS_ENABLED:
        return

    if instance.room.gig:
        gig_search_indexes.update_gig_search_index(instance.room.gig)

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
