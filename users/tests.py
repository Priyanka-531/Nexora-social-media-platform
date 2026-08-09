from django.test import TestCase, Client
from django.contrib.auth.models import User
from users.models import Profile
from users.services import UserService


class UserServiceTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="testuser1", password="password123")
        self.user2 = User.objects.create_user(username="testuser2", password="password123")

    def test_profile_signal_creation(self):
        """Verify profile auto-creation via signal on user save."""
        profile = Profile.objects.filter(user=self.user1).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user.username, "testuser1")

    def test_get_feed_data(self):
        """Verify feed data retrieval service."""
        feed_data = UserService.get_feed_data(self.user1)
        self.assertIn("posts", feed_data)
        self.assertIn("suggested_users", feed_data)
        self.assertIn(self.user2, feed_data["suggested_users"])

    def test_get_profile_data(self):
        """Verify profile context compilation."""
        profile_data = UserService.get_profile_data(self.user1, "testuser2")
        self.assertEqual(profile_data["profile_user"], self.user2)
        self.assertFalse(profile_data["is_following"])
        self.assertEqual(profile_data["followers_count"], 0)
