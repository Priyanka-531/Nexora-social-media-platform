import os
import urllib.request
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from posts.models import Story


class Command(BaseCommand):
    help = "Creates multi-slide Instagram-style demo stories tailored to each profile profession with 24-hour expiration."

    DEMO_STORIES = {
        "nexora_creator": [
            {
                "caption": "Behind the scenes recording today's video campaign! 🎥✨",
                "image_url": "https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Editing timeline & color grading setup for Episode 12 💻🎬",
                "image_url": "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Setting up podcast studio for afternoon interview 🎙️☕",
                "image_url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&auto=format&fit=crop&q=80",
            },
        ],
        "nexora_dev": [
            {
                "caption": "Building fullstack Django apps & scalable cloud backend services 💻🚀",
                "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "All unit tests passing cleanly! Time to push to main branch ⚡",
                "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&auto=format&fit=crop&q=80",
            },
        ],
        "design_with_riya": [
            {
                "caption": "Exploring dark mode UI components & glassmorphism color palettes 🎨📱",
                "image_url": "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Refining typography hierarchy and mobile component swatches ✨",
                "image_url": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&auto=format&fit=crop&q=80",
            },
        ],
        "tech_aarav": [
            {
                "caption": "Unboxing & testing the latest desk setup gadgets ⚡🎧",
                "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Wireless mechanical keyboard & ergonomic mouse review coming soon ⌨️🖱️",
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
            },
        ],
        "travel_with_anaya": [
            {
                "caption": "Sunrise over the mountain misty valley 🏔️🌅",
                "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Morning coffee views on the mountain stay balcony ☕🏡",
                "image_url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Winding road drive to the next coastal village 🚗🌊",
                "image_url": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&auto=format&fit=crop&q=80",
            },
        ],
        "code_with_rohan": [
            {
                "caption": "Late night coding session & fresh hot coffee ☕💻",
                "image_url": "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Building interactive REST APIs with Python & Django 🚀",
                "image_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&auto=format&fit=crop&q=80",
            },
        ],
        "photography_meera": [
            {
                "caption": "Golden hour urban street portrait 📸🌆",
                "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Loaded 35mm film camera for street light reflections 🎞️✨",
                "image_url": "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=800&auto=format&fit=crop&q=80",
            },
        ],
        "fitness_kabir": [
            {
                "caption": "Morning workout motivation - Consistency over perfection! 🏋️‍♂️💪",
                "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Post-workout meal prep: High protein bowl 🥗🍗",
                "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&auto=format&fit=crop&q=80",
            },
        ],
        "art_by_sana": [
            {
                "caption": "Work in progress - Acrylic canvas digital painting 🎨✨",
                "image_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Detailing pastel brush strokes & gold foil highlights 🖌️🌟",
                "image_url": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=800&auto=format&fit=crop&q=80",
            },
        ],
        "music_arjun": [
            {
                "caption": "Mixing new lo-fi ambient beats in the studio 🎧🎵",
                "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
            },
            {
                "caption": "Synthesizer keyboard melodies & studio headphones 🎹🔊",
                "image_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80",
            },
        ],
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Creating multi-slide Instagram-style demo stories tailored to professions..."))

        stories_dir = os.path.join(settings.MEDIA_ROOT, "stories")
        os.makedirs(stories_dir, exist_ok=True)

        # Clear old demo stories to prevent stale duplicates
        Story.objects.all().delete()

        created_count = 0

        for username, slides in self.DEMO_STORIES.items():
            user = User.objects.filter(username=username).first()
            if not user:
                continue

            for idx, slide in enumerate(slides, start=1):
                img_filename = f"{username}_story_slide_{idx}.jpg"
                img_filepath = os.path.join(stories_dir, img_filename)

                try:
                    req = urllib.request.Request(
                        slide["image_url"],
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    with urllib.request.urlopen(req) as response, open(img_filepath, 'wb') as out_file:
                        out_file.write(response.read())
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Could not download story image for @{username} slide {idx}: {e}"))

                story = Story.objects.create(
                    author=user,
                    caption=slide["caption"],
                    expires_at=timezone.now() + timedelta(hours=24),
                )

                if os.path.exists(img_filepath):
                    story.image = f"stories/{img_filename}"
                
                story.save()
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created story slide {idx} for @{username}"))

        self.stdout.write(self.style.SUCCESS(f"\nCompleted! Total active story slides created: {created_count}."))
