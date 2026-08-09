from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
from interactions.models import Follow, FollowRequest, Notification


class Command(BaseCommand):
    help = "Creates realistic dummy follow requests for testing the Follow Request system."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Ensuring demo accounts are initialized..."))
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

        demo_users = list(User.objects.filter(username__in=demo_usernames))

        if not demo_users:
            self.stdout.write(self.style.ERROR("No demo users found."))
            return

        all_users = User.objects.all()

        requests_created = 0

        for target_user in all_users:
            # Pick demo senders who are not target_user
            senders = [u for u in demo_users if u != target_user][:4]

            for sender in senders:
                # Remove existing follow relationship if present so request is pending
                Follow.objects.filter(follower=sender, following=target_user).delete()

                req, created = FollowRequest.objects.get_or_create(
                    sender=sender,
                    receiver=target_user
                )
                req.status = "pending"
                req.save()

                Notification.objects.get_or_create(
                    recipient=target_user,
                    sender=sender,
                    notification_type="follow_request"
                )
                requests_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {requests_created} realistic pending follow requests across users!"
            )
        )
