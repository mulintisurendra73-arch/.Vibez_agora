from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class AuthenticationPageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_registration_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_registration_creates_user(self):
        response = self.client.post(reverse("register"), {
            "username": "test_listener", "display_name": "Test Listener", "email": "listener@example.com",
            "password1": "Orbit!Cedar9_Marble", "password2": "Orbit!Cedar9_Marble",
        })
        self.assertRedirects(response, reverse("login"))
        user = get_user_model().objects.get(username="test_listener")
        self.assertEqual(user.first_name, "Test Listener")
        self.assertTrue(user.check_password("Orbit!Cedar9_Marble"))

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
