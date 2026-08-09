from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from posts.models import Post
from posts.services import PostService


class PostServiceTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="author", password="password123")
        image_content = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        uploaded_image = SimpleUploadedFile("test.gif", image_content, content_type="image/gif")
        self.post = Post.objects.create(author=self.user, image=uploaded_image, caption="Test post")

    def test_toggle_like(self):
        """Verify liking and unliking post."""
        success, liked, count = PostService.toggle_like(self.user, self.post.id)
        self.assertTrue(success)
        self.assertTrue(liked)
        self.assertEqual(count, 1)

        success, liked, count = PostService.toggle_like(self.user, self.post.id)
        self.assertTrue(success)
        self.assertFalse(liked)
        self.assertEqual(count, 0)

    def test_toggle_save(self):
        """Verify bookmarking and un-bookmarking post."""
        success, saved, msg = PostService.toggle_save(self.user, self.post.id)
        self.assertTrue(success)
        self.assertTrue(saved)

        success, saved, msg = PostService.toggle_save(self.user, self.post.id)
        self.assertTrue(success)
        self.assertFalse(saved)

    def test_delete_post_unauthorized(self):
        """Verify unauthorized user cannot delete post."""
        other_user = User.objects.create_user(username="other", password="password123")
        success, message, code = PostService.delete_post(other_user, self.post.id)
        self.assertFalse(success)
        self.assertEqual(code, 403)
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_authorized(self):
        """Verify author can delete post."""
        success, message, code = PostService.delete_post(self.user, self.post.id)
        self.assertTrue(success)
        self.assertEqual(code, 200)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_controller_form_redirect(self):
        """Verify HTML form POST request to delete_post redirects to referrer/home."""
        self.client.login(username="author", password="password123")
        url = reverse("delete_post", kwargs={"post_id": self.post.id})
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse("home"))
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_controller_ajax_json(self):
        """Verify AJAX POST request to delete_post returns JSON response."""
        self.client.login(username="author", password="password123")
        url = reverse("delete_post", kwargs={"post_id": self.post.id})
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
