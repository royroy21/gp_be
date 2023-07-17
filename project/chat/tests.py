import json
from datetime import timedelta

from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from project.chat import models
from project.core import tests as core_tests
from project.core.asgi import application
from project.country import models as country_models
from project.gig import models as gig_models


class ChannelsTestCase(TransactionTestCase):
    """
    Using this to avoid the dreaded connection already closed error.
    https://github.com/django/channels/issues/1110
    """

    # If transactions aren't available, Django will serialize the database
    # contents into a fixture during setup and flush and reload them
    # during teardown (as flush does not restore data from migrations).
    # This can be slow; this flag allows enabling on a per-case basis.
    serialized_rollback = True


def create_user_and_token(username):
    """
    Helper function as channels requires JWT only.
    """
    user, auth_header = core_tests.setup_user_with_jwt_headers(username)
    token = auth_header[core_tests.AUTH_HEADER_NAME].split(" ")[1]
    return user, token


class ChatTestCase(ChannelsTestCase):
    def setUp(self):
        self.fred, self.fred_token = create_user_and_token("fred")
        self.jiggy, self.jiggy_token = create_user_and_token("jiggy")
        country = country_models.CountryCode.objects.create(
            country="United Kingdom",
            code="GB",
        )
        self.fred_gig = gig_models.Gig.objects.create(
            user=self.fred,
            title="Man Feelings",
            location="Brixton academy",
            country=country,
            start_date=timezone.now() - timedelta(hours=1),
        )
        self.room = models.Room.objects.create(
            user=self.fred,
            type=models.GIG,
        )

    async def test_send_message_when_unauthenticated(self):
        room = "99"
        communicator = WebsocketCommunicator(
            application=application,
            path=f"ws/chat/{room}/?token=cats",
        )
        connected, sub_protocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_send_message_when_no_token_is_sent(self):
        room = "99"
        communicator = WebsocketCommunicator(
            application=application,
            path=f"ws/chat/{room}/",
        )
        connected, sub_protocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_initiate_new_direct_chat(self):
        path = (
            f"ws/new_chat/?token={self.jiggy_token}"
            f"&type=direct&to_user_id={self.fred.id}"
        )
        communicator = WebsocketCommunicator(
            application=application,
            path=path,
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        message = "hello Fred!"
        await communicator.send_json_to(data={"message": message})
        # First we receive a message from the server
        # regarding which room to connect to.
        response = await communicator.receive_from()
        await communicator.disconnect()

        # Check Room database entry is created and returned.
        room = json.loads(response)["room"]
        room_query = await sync_to_async(models.Room.objects.filter)(
            id=room["id"],
            user=self.jiggy,
            type=models.DIRECT,
        )
        room_exists = await sync_to_async(room_query.exists)()
        self.assertTrue(room_exists)

        # Check Room membership.
        members = await sync_to_async(room_query.values_list)(
            "members__id",
            flat=True,
        )
        members_list = await sync_to_async(list)(members)
        self.assertEqual(len(members_list), 2)
        self.assertIn(self.jiggy.id, members_list)
        self.assertIn(self.fred.id, members_list)

    async def test_send_message_to_room_that_does_not_exist(self):
        room = "cats"
        communicator = WebsocketCommunicator(
            application=application,
            path=f"ws/chat/{room}/?token={self.jiggy_token}&type=DIRECT",
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_initiate_new_chat_in_response_to_gig(self):
        path = (
            f"ws/new_chat/?token={self.jiggy_token}"
            f"&type=gig&gig_id={self.fred_gig.id}"
        )
        communicator = WebsocketCommunicator(
            application=application,
            path=path,
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        message = "hello Fred!"
        await communicator.send_json_to(data={"message": message})
        # First we receive a message from the server
        # regarding which room to connect to.
        response = await communicator.receive_from()
        await communicator.disconnect()

        # Check Room database entry is created and returned.
        room = json.loads(response)["room"]
        room_query = await sync_to_async(models.Room.objects.filter)(
            id=room["id"],
            user=self.jiggy,
            type=models.GIG,
            gig=self.fred_gig,
        )
        room_exists = await sync_to_async(room_query.exists)()
        self.assertTrue(room_exists)

        # Check Room membership.
        members = await sync_to_async(room_query.values_list)(
            "members__id",
            flat=True,
        )
        members_list = await sync_to_async(list)(members)
        self.assertEqual(len(members_list), 2)
        self.assertIn(self.jiggy.id, members_list)
        self.assertIn(self.fred.id, members_list)

    async def test_send_message_to_existing_room(self):
        path = f"ws/chat/{self.room.id}/?token={self.jiggy_token}&type=direct"
        communicator = WebsocketCommunicator(
            application=application,
            path=path,
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        message = "hello Fred!"
        await communicator.send_json_to(data={"message": message})
        await communicator.disconnect()

        # Check no new rooms were created.
        rooms_count = await sync_to_async(models.Room.objects.count)()
        self.assertEqual(rooms_count, 1)

        # Check existing room has a new message.
        message_query = await sync_to_async(models.Message.objects.filter)(
            user=self.jiggy,
            room=self.room,
            message=message,
        )
        message_exists = await sync_to_async(message_query.exists)()
        self.assertTrue(message_exists)

    async def test_send_message_from_one_client_to_another(self):
        path = f"ws/chat/{self.room.id}/"
        communicator_1 = WebsocketCommunicator(
            application=application,
            path=path + "?token=" + self.jiggy_token,
        )
        communicator_2 = WebsocketCommunicator(
            application=application,
            path=path + "?token=" + self.fred_token,
        )
        connected_1, _ = await communicator_1.connect()
        self.assertTrue(connected_1)
        connected2, _ = await communicator_2.connect()
        self.assertTrue(connected2)

        message = "hello Fred!"
        await communicator_1.send_json_to(data={"message": message})

        response1 = await communicator_1.receive_from()
        self.assertEqual(json.loads(response1)["message"], message)
        response2 = await communicator_2.receive_from()
        self.assertEqual(json.loads(response2)["message"], message)

        await communicator_1.disconnect()
        await communicator_2.disconnect()


class TestMessageViewSet(TestCase):
    def setUp(self):
        self.fred, self.fred_client = core_tests.setup_user_with_drf_client(
            username="fred",
        )
        self.jiggy = core_tests.create_user(username="jiggy")
        self.room = models.Room.objects.create(
            user=self.fred,
            type=models.DIRECT,
        )
        self.room.members.add(self.fred, self.jiggy)
        self.messages = [
            {"user": self.fred, "message": "first_message"},
            {"user": self.jiggy, "message": "second_message"},
            {"user": self.fred, "message": "third_message"},
            {"user": self.jiggy, "message": "forth_message"},
            {"user": self.fred, "message": "fifth_message"},
        ]
        for message in self.messages:
            models.Message.objects.create(
                room=self.room,
                user=message["user"],
                message=message["message"],
            )

    def test_getting_messages_when_user_is_not_member_of_room(self):
        user, drf_client = core_tests.setup_user_with_drf_client(
            username="bungle",
        )
        response = drf_client.get(
            path=reverse("message-api-list") + f"?room_id={self.room.id}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_messages_for_room(self):
        response = self.fred_client.get(
            path=reverse("message-api-list") + f"?room_id={self.room.id}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["count"], 5)
        self.assertEqual(data["previous"], None)
        self.assertIn("next", data)

        messages_reversed = list(reversed(self.messages))
        results = data["results"]
        for n, result in enumerate(results):
            self.assertEqual(
                result["user"]["id"], messages_reversed[n]["user"].id
            )
            self.assertEqual(
                result["message"], messages_reversed[n]["message"]
            )
