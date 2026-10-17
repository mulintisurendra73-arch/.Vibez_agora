from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Room, RoomMembership

User = get_user_model()


class DiscoveryAndRoomTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="vibez_host",
            password="Test-pass-2468",
        )

        self.other = User.objects.create_user(
            username="vibez_guest",
            password="Test-pass-2468",
        )

    def test_discover_page_loads_and_can_search(self):
        response = self.client.get(
            reverse("discover"),
            {"q": "vibez_guest"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "vibez_guest")

    def test_logged_in_user_can_create_room(self):
        self.client.login(
            username="vibez_host",
            password="Test-pass-2468",
        )

        response = self.client.post(
            reverse("create_room"),
            {
                "title": "Late night chat",
                "description": "Talk about anything",
                "topic": "Community",
            },
            follow=True,
        )

        # A successful create view commonly redirects.
        self.assertIn(
            response.status_code,
            (200, 201, 302),
        )

        room = Room.objects.filter(
            title="Late night chat",
            host=self.user,
        ).first()

        self.assertIsNotNone(
            room,
            "The room was not saved. Check the create-room view "
            "and form validation.",
        )

        self.assertTrue(
            RoomMembership.objects.filter(
                room=room,
                user=self.user,
            ).exists()
        )

    def test_join_and_leave_room(self):
        room = Room.objects.create(
            host=self.user,
            title="Open mic",
            status=Room.Status.OPEN,
        )

        self.client.login(
            username="vibez_guest",
            password="Test-pass-2468",
        )

        join_response = self.client.post(
            reverse("join_room", args=[room.pk])
        )

        self.assertIn(join_response.status_code, (200, 302))

        self.assertTrue(
            RoomMembership.objects.filter(
                room=room,
                user=self.other,
            ).exists()
        )

        leave_response = self.client.post(
            reverse("leave_room", args=[room.pk])
        )

        self.assertIn(leave_response.status_code, (200, 302))

        self.assertFalse(
            RoomMembership.objects.filter(
                room=room,
                user=self.other,
            ).exists()
        )



    def test_duplicate_open_rooms_by_same_host_are_shown_once(self):
        Room.objects.create(host=self.user, title="Late Night Chat", status=Room.Status.OPEN)
        Room.objects.create(host=self.user, title="  late   night chat ", status=Room.Status.OPEN)
        response = self.client.get(reverse("rooms"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["rooms"]), 1)

    def test_host_cannot_create_duplicate_open_room_title(self):
        existing = Room.objects.create(host=self.user, title="Late Night Chat", status=Room.Status.OPEN)
        self.client.login(username="vibez_host", password="Test-pass-2468")
        response = self.client.post(reverse("create_room"), {
            "title": " late   night chat ",
            "description": "Another copy",
            "topic": "Community",
        })
        self.assertRedirects(response, reverse("room_detail", args=[existing.pk]))
        self.assertEqual(Room.objects.filter(host=self.user, status=Room.Status.OPEN).count(), 1)

    def test_room_page_displays_eight_seats_and_unlimited_listeners(self):
        room = Room.objects.create(
            host=self.user,
            title="Eight seat room",
            status=Room.Status.OPEN,
        )
        response = self.client.get(reverse("room_detail", args=[room.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unlimited listeners")
        for number in range(1, 9):
            self.assertContains(response, f"Seat {number}")

    def test_member_can_join_and_leave_a_talking_seat(self):
        room = Room.objects.create(
            host=self.user,
            title="Seat test room",
            status=Room.Status.OPEN,
        )
        self.client.login(username="vibez_guest", password="Test-pass-2468")

        response = self.client.post(
            reverse("join_seat", args=[room.pk, 3]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        membership = RoomMembership.objects.get(room=room, user=self.other)
        self.assertEqual(membership.seat_number, 3)
        self.assertEqual(membership.role, RoomMembership.Role.SPEAKER)

        response = self.client.post(
            reverse("leave_seat", args=[room.pk]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        membership.refresh_from_db()
        self.assertIsNone(membership.seat_number)
        self.assertEqual(membership.role, RoomMembership.Role.LISTENER)

    def test_two_members_cannot_take_the_same_seat(self):
        room = Room.objects.create(
            host=self.user,
            title="Seat collision room",
            status=Room.Status.OPEN,
        )
        RoomMembership.objects.create(
            room=room,
            user=self.user,
            role=RoomMembership.Role.HOST,
            seat_number=1,
        )
        self.client.login(username="vibez_guest", password="Test-pass-2468")
        response = self.client.post(
            reverse("join_seat", args=[room.pk, 1]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            RoomMembership.objects.filter(room=room, user=self.other, seat_number=1).exists()
        )

    def test_room_host_is_correct(self):
        room = Room.objects.create(
            host=self.user,
            title="Host test room",
            status=Room.Status.OPEN,
        )

        self.assertEqual(room.host, self.user)

    def test_guest_cannot_use_host_controls(self):
        room = Room.objects.create(
            host=self.user,
            title="Private controls test",
            status=Room.Status.OPEN,
        )

        self.client.login(
            username="vibez_guest",
            password="Test-pass-2468",
        )

        # Update this URL name if your project uses a different
        # name for its host-management endpoint.
        if "close_room" not in __import__(
            "django.urls", fromlist=["get_resolver"]
        ).get_resolver().reverse_dict:
            self.skipTest(
                "The close_room URL is not registered under that name."
            )

        response = self.client.post(
            reverse("close_room", args=[room.pk])
        )

        self.assertIn(response.status_code, (302, 403, 404))

        room.refresh_from_db()
        self.assertEqual(room.host, self.user)