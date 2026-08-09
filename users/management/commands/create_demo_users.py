import os
import urllib.request
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from users.models import Profile
from interactions.models import Follow


class Command(BaseCommand):
    help = "Creates 10 realistic demo accounts with unique profile pictures and follow relationships."

    DEMO_USERS = [
        {
            "username": "nexora_creator",
            "first_name": "Ananya",
            "last_name": "Verma",
            "bio": "Creating digital experiences & visual stories on Nexora ✨",
            "profession": "Content Creator",
            "location": "Mumbai, India",
            "college": "NIFT Mumbai",
            "website": "https://nexora.com/ananya",
            "avatar_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&auto=format&fit=crop&q=80",
            "follows": ["design_with_riya", "tech_aarav", "travel_with_anaya", "photography_meera"],
        },
        {
            "username": "nexora_dev",
            "first_name": "Aarav",
            "last_name": "Sharma",
            "bio": "Building fullstack apps with Python, Django, and modern JS 💻",
            "profession": "Lead Developer",
            "location": "Bengaluru, India",
            "college": "IIT Bombay",
            "website": "https://github.com/aarav-dev",
            "avatar_url": "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&auto=format&fit=crop&q=80",
            "follows": ["code_with_rohan", "tech_aarav", "nexora_creator"],
        },
        {
            "username": "design_with_riya",
            "first_name": "Riya",
            "last_name": "Kapoor",
            "bio": "Passionate about UI/UX, design systems, and glassmorphic aesthetics 🎨",
            "profession": "UI/UX Designer",
            "location": "Delhi, India",
            "college": "NID Ahmedabad",
            "website": "https://dribbble.com/riya_design",
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
            "follows": ["art_by_sana", "photography_meera", "nexora_creator"],
        },
        {
            "username": "tech_aarav",
            "first_name": "Aarav",
            "last_name": "Mehta",
            "bio": "Exploring the future of tech, AI gadgets, and developer tools 🚀",
            "profession": "Tech Reviewer",
            "location": "Pune, India",
            "college": "COEP Pune",
            "website": "https://youtube.com/@techaarav",
            "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80",
            "follows": ["nexora_dev", "code_with_rohan", "music_arjun"],
        },
        {
            "username": "travel_with_anaya",
            "first_name": "Anaya",
            "last_name": "Joshi",
            "bio": "Capturing mountain sunsets and coastal breezes around the world 🏔️🌊",
            "profession": "Travel Blogger",
            "location": "Manali, India",
            "college": "Delhi University",
            "website": "https://travelwithanaya.com",
            "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80",
            "follows": ["photography_meera", "fitness_kabir", "design_with_riya"],
        },
        {
            "username": "code_with_rohan",
            "first_name": "Rohan",
            "last_name": "Patel",
            "bio": "Clean code enthusiast & open source contributor ☕",
            "profession": "Software Engineer",
            "location": "Hyderabad, India",
            "college": "IIIT Hyderabad",
            "website": "https://rohanpatel.dev",
            "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80",
            "follows": ["nexora_dev", "tech_aarav", "art_by_sana"],
        },
        {
            "username": "photography_meera",
            "first_name": "Meera",
            "last_name": "Nair",
            "bio": "Portraits, urban street photography, and golden hour light 📸",
            "profession": "Photographer",
            "location": "Kochi, India",
            "college": "Loyola College",
            "website": "https://instagram.com/meera_clicks",
            "avatar_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&auto=format&fit=crop&q=80",
            "follows": ["travel_with_anaya", "art_by_sana", "nexora_creator"],
        },
        {
            "username": "fitness_kabir",
            "first_name": "Kabir",
            "last_name": "Singh",
            "bio": "Helping you stay disciplined, fit, and healthy 🏋️‍♂️",
            "profession": "Fitness Coach",
            "location": "Chandigarh, India",
            "college": "Panjab University",
            "website": "https://kabirfit.com",
            "avatar_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&auto=format&fit=crop&q=80",
            "follows": ["travel_with_anaya", "music_arjun", "nexora_creator"],
        },
        {
            "username": "art_by_sana",
            "first_name": "Sana",
            "last_name": "Khan",
            "bio": "Digital art, illustrations, and pastel canvas paintings 🎨✨",
            "profession": "Visual Artist",
            "location": "Jaipur, India",
            "college": "JJ School of Art",
            "website": "https://artbysana.com",
            "avatar_url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=400&auto=format&fit=crop&q=80",
            "follows": ["design_with_riya", "photography_meera", "nexora_creator"],
        },
        {
            "username": "music_arjun",
            "first_name": "Arjun",
            "last_name": "Malhotra",
            "bio": "Lo-fi beats, ambient sounds, and indie music production 🎧🎵",
            "profession": "Music Producer",
            "location": "Goa, India",
            "college": "NMIMS Mumbai",
            "website": "https://soundcloud.com/arjunmusic",
            "avatar_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&auto=format&fit=crop&q=80",
            "follows": ["nexora_creator", "tech_aarav", "code_with_rohan"],
        },
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting creation and profile picture download for demo accounts..."))
        
        media_dir = os.path.join(settings.MEDIA_ROOT, "profile_pictures")
        os.makedirs(media_dir, exist_ok=True)

        user_objects = {}

        for data in self.DEMO_USERS:
            username = data["username"]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                }
            )
            if created:
                user.set_password("NexoraDemo123!")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created new user: @{username}"))
            else:
                user.first_name = data["first_name"]
                user.last_name = data["last_name"]
                user.save()

            user_objects[username] = user

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = data["bio"]
            profile.profession = data["profession"]
            profile.location = data["location"]
            profile.college = data["college"]
            profile.website = data["website"]

            # Save distinct profile image
            img_filename = f"{username}_avatar.jpg"
            img_filepath = os.path.join(media_dir, img_filename)

            if not os.path.exists(img_filepath):
                try:
                    req = urllib.request.Request(
                        data["avatar_url"],
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    with urllib.request.urlopen(req) as response, open(img_filepath, 'wb') as out_file:
                        out_file.write(response.read())
                    self.stdout.write(self.style.SUCCESS(f"Downloaded profile picture for @{username}"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to download image for @{username}: {e}"))

            if os.path.exists(img_filepath):
                profile.profile_picture = f"profile_pictures/{img_filename}"

            profile.save()

        # Build Follow Graph
        self.stdout.write(self.style.NOTICE("Establishing follow connections between demo accounts..."))
        follows_created = 0

        for data in self.DEMO_USERS:
            follower = user_objects.get(data["username"])
            if not follower:
                continue

            for target_username in data["follows"]:
                target_user = user_objects.get(target_username)
                if target_user and target_user != follower:
                    _, created = Follow.objects.get_or_create(follower=follower, following=target_user)
                    if created:
                        follows_created += 1

        # Also connect existing non-demo users (e.g. current user) with demo accounts
        non_demo_users = User.objects.exclude(username__in=[d["username"] for d in self.DEMO_USERS])
        for other_user in non_demo_users:
            # Have 3 demo accounts follow this user
            demo_followers = list(user_objects.values())[:3]
            for demo_u in demo_followers:
                if demo_u != other_user:
                    Follow.objects.get_or_create(follower=demo_u, following=other_user)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDemo accounts setup completed! Created follow connections: {follows_created}."
            )
        )
