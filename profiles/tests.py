from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Profile, Follow, Block, UserReport, Notification

User = get_user_model()

class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="listener1", email="one@example.com", password="StrongPass!928", first_name="Listener One")
        self.other = User.objects.create_user(username="listener2", email="two@example.com", password="StrongPass!928", first_name="Listener Two")

    def test_profile_created_for_new_user(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_profile_requires_login(self):
        response = self.client.get(reverse("my_profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_user_can_edit_own_profile(self):
        self.client.login(username="listener1", password="StrongPass!928")
        response = self.client.post(reverse("edit_profile"), {
            "display_name": "Updated Name", "email": "one@example.com", "bio": "I enjoy good conversations.",
        })
        self.assertRedirects(response, reverse("my_profile"))
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated Name")
        self.assertEqual(self.user.profile.bio, "I enjoy good conversations.")

    def test_follow_and_unfollow(self):
        self.client.login(username="listener1", password="StrongPass!928")
        url = reverse("toggle_follow", kwargs={"username": self.other.username})
        self.client.post(url)
        self.assertTrue(Follow.objects.filter(follower=self.user, followed=self.other).exists())
        self.client.post(url)
        self.assertFalse(Follow.objects.filter(follower=self.user, followed=self.other).exists())

    def test_cannot_follow_self(self):
        self.client.login(username="listener1", password="StrongPass!928")
        self.client.post(reverse("toggle_follow", kwargs={"username": self.user.username}))
        self.assertFalse(Follow.objects.filter(follower=self.user, followed=self.user).exists())


class SafetyAndNotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="safety1", email="s1@example.com", password="StrongPass!928")
        self.other = User.objects.create_user(username="safety2", email="s2@example.com", password="StrongPass!928")
        self.client.login(username="safety1", password="StrongPass!928")

    def test_user_can_make_profile_private(self):
        response = self.client.post(reverse("edit_profile"), {"display_name": "Safety One", "email": "s1@example.com", "bio": "private bio", "is_private": "on"})
        self.assertRedirects(response, reverse("my_profile"))
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.is_private)

    def test_private_profile_hides_details_from_non_follower(self):
        self.other.profile.is_private = True
        self.other.profile.bio = "secret bio"
        self.other.profile.save()
        response = self.client.get(reverse("public_profile", kwargs={"username": self.other.username}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_view_profile"])
        self.assertNotContains(response, "secret bio")

    def test_block_removes_follow_relationship_and_hides_profile(self):
        Follow.objects.create(follower=self.user, followed=self.other)
        response = self.client.post(reverse("toggle_block", kwargs={"username": self.other.username}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Block.objects.filter(blocker=self.user, blocked=self.other).exists())
        self.assertFalse(Follow.objects.filter(follower=self.user, followed=self.other).exists())
        profile_response = self.client.get(reverse("public_profile", kwargs={"username": self.other.username}))
        self.assertFalse(profile_response.context["can_view_profile"])

    def test_report_is_saved_for_moderator_review(self):
        response = self.client.post(reverse("report_user", kwargs={"username": self.other.username}), {"reason": "spam", "details": "Repeated spam"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserReport.objects.filter(reporter=self.user, reported_user=self.other, reason="spam", reviewed=False).exists())

    def test_follow_creates_notification(self):
        self.client.post(reverse("toggle_follow", kwargs={"username": self.other.username}))
        self.assertTrue(Notification.objects.filter(recipient=self.other, actor=self.user, kind="follow").exists())

    def test_notifications_page_marks_items_read(self):
        item = Notification.objects.create(recipient=self.user, actor=self.other, kind="follow", message="Safety Two started following you.")
        response = self.client.get(reverse("notifications"))
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertTrue(item.is_read)
