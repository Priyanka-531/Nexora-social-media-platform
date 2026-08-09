from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
from posts.models import Post
from interactions.models import Notification
from interactions.services import NotificationService


class Command(BaseCommand):
    help = "Creates realistic dummy notifications (likes, comments, mentions, follows) for testing."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Ensuring demo accounts exist..."))
        try:
            call_command("create_demo_users")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Note on create_demo_users: {e}"))

        demo_usernames = [
            "design_with_riya",
            "tech_aarav",
            "travel_with_anaya",
            "art_by_sana",
            "music_arjun",
            "code_with_rohan",
        ]

        demo_users = {u.username: u for u in User.objects.filter(username__in=demo_usernames)}

        if not demo_users:
            self.stdout.write(self.style.ERROR("No demo users found."))
            return

        all_users = User.objects.all()
        created_count = 0

        for target_user in all_users:
            # Find target user's posts or recent posts
            user_posts = list(Post.objects.filter(author=target_user))
            any_posts = list(Post.objects.all())

            # 1. Like notification
            if "design_with_riya" in demo_users:
                sender = demo_users["design_with_riya"]
                post = user_posts[0] if user_posts else (any_posts[0] if any_posts else None)
                if sender != target_user:
                    n = NotificationService.create_notification(target_user, sender, "like", post=post)
                    if n: created_count += 1

            # 2. Comment notification
            if "tech_aarav" in demo_users:
                sender = demo_users["tech_aarav"]
                post = user_posts[0] if user_posts else (any_posts[0] if any_posts else None)
                if sender != target_user:
                    n = NotificationService.create_notification(target_user, sender, "comment", post=post)
                    if n: created_count += 1

            # 3. Mention notification
            if "code_with_rohan" in demo_users:
                sender = demo_users["code_with_rohan"]
                post = any_posts[0] if any_posts else None
                if sender != target_user:
                    n = NotificationService.create_notification(target_user, sender, "mention", post=post)
                    if n: created_count += 1

            # 4. New follower notification
            if "art_by_sana" in demo_users:
                sender = demo_users["art_by_sana"]
                if sender != target_user:
                    n = NotificationService.create_notification(target_user, sender, "new_follower")
                    if n: created_count += 1

            # 5. Follow accept notification
            if "music_arjun" in demo_users:
                sender = demo_users["music_arjun"]
                if sender != target_user:
                    n = NotificationService.create_notification(target_user, sender, "follow_accept")
                    if n: created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {created_count} realistic dummy notifications!"
            )
        )
