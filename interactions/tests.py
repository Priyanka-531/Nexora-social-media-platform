from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Post
from interactions.models import Comment, Follow, FollowRequest
from interactions.services import InteractionService


class InteractionServiceTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        image_content = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        uploaded_image = SimpleUploadedFile("test.gif", image_content, content_type="image/gif")
        self.post = Post.objects.create(author=self.user1, image=uploaded_image, caption="Interaction post")

    def test_add_and_delete_comment(self):
        """Test adding and deleting comments via InteractionService."""
        success, data, code = InteractionService.add_comment(self.post.id, self.user2, "Nice picture!")
        self.assertTrue(success)
        self.assertEqual(code, 200)
        self.assertEqual(data["comment_count"], 1)

        comment_id = data["comment"]["id"]
        # Unauthorized delete attempt
        success_del, data_del, code_del = InteractionService.delete_comment(comment_id, self.user1)
        self.assertFalse(success_del)
        self.assertEqual(code_del, 403)

        # Authorized delete attempt
        success_del, data_del, code_del = InteractionService.delete_comment(comment_id, self.user2)
        self.assertTrue(success_del)
        self.assertEqual(data_del["comment_count"], 0)

    def test_toggle_follow(self):
        """Test automatic follow, unfollow, and follow request accept/reject workflows."""
        # 1. Self-follow attempt -> Prevented
        success, status_str, is_following, is_requested, t_followers, t_following, f_following, message = InteractionService.toggle_follow(self.user1, "user1")
        self.assertFalse(success)

        # 2. Valid follow action -> Automatically follows immediately (status="following")
        success, status_str, is_following, is_requested, t_followers, t_following, f_following, message = InteractionService.toggle_follow(self.user1, "user2")
        self.assertTrue(success)
        self.assertEqual(status_str, "following")
        self.assertTrue(is_following)
        self.assertFalse(is_requested)
        self.assertTrue(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

        # 3. Follow Request Accept/Reject Workflow test
        req = FollowRequest.objects.create(sender=self.user2, receiver=self.user1, status="pending")
        acc_success, acc_data, acc_code = InteractionService.accept_follow_request(self.user1, req.id)
        self.assertTrue(acc_success)
        self.assertEqual(acc_code, 200)
        self.assertTrue(Follow.objects.filter(follower=self.user2, following=self.user1).exists())

        # 4. Unfollow -> removes Follow
        success, status_str, is_following, is_requested, t_followers, t_following, f_following, message = InteractionService.toggle_follow(self.user1, "user2")
        self.assertTrue(success)
        self.assertEqual(status_str, "none")
        self.assertFalse(is_following)
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())
        self.assertTrue(success)
        self.assertEqual(status_str, "none")
        self.assertFalse(is_following)
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_reject_follow_request(self):
        """Test rejecting a follow request does not create Follow."""
        req = FollowRequest.objects.create(sender=self.user1, receiver=self.user2, status="pending")
        rej_success, rej_data, rej_code = InteractionService.reject_follow_request(self.user2, req.id)
        self.assertTrue(rej_success)
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

