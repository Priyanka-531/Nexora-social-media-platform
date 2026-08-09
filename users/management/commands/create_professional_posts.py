import os
import urllib.request
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from posts.models import Post
from interactions.models import Comment, Follow
from interactions.services import NotificationService


class Command(BaseCommand):
    help = "Creates realistic professional posts with high quality images, likes, and peer comments."

    PROFESSIONAL_POSTS = [
        {
            "username": "design_with_riya",
            "caption": "Crafted a new Glassmorphic Design System for Nexora! Soft gradients, ambient elevation shadows, and clean typography make all the difference. What do you think of this aesthetic? 🎨✨ #uiux #designsystem #glassmorphism #nexora @nexora_creator",
            "image_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&auto=format&fit=crop&q=80",
            "filename": "post_design_glassmorphism.jpg",
            "comments": [
                ("nexora_creator", "This looks insanely clean Riya! The elevation shadows are spot on 👌"),
                ("nexora_dev", "Awesome UI work! Integrating these clean tokens in Django templates was super smooth."),
                ("art_by_sana", "Love the pastel color palette! Modern and elegant ✨"),
            ]
        },
        {
            "username": "nexora_dev",
            "caption": "Optimized our Django ORM querysets with select_related and prefetch_related! Database query latency dropped from 140ms to 12ms flat ⚡ Python + Django powers Nexora effortlessly! #django #python #backend #webdev @code_with_rohan",
            "image_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&auto=format&fit=crop&q=80",
            "filename": "post_django_dev.jpg",
            "comments": [
                ("code_with_rohan", "N+1 query fixes are the best feeling! Great performance boost 🚀"),
                ("tech_aarav", "12ms response time is super fast! Nice work Aarav."),
            ]
        },
        {
            "username": "travel_with_anaya",
            "caption": "Sunrise over the Himalayan peaks this morning! Nothing beats crisp mountain air and golden horizon views 🏔️✨ Pack your bags and explore! #travel #himalayas #mountains #wanderlust @photography_meera",
            "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&auto=format&fit=crop&q=80",
            "filename": "post_travel_himalayas.jpg",
            "comments": [
                ("photography_meera", "Breathtaking lighting on those mountain ridges! Incredible capture Meera 📸"),
                ("fitness_kabir", "That mountain trek must have been an incredible cardio workout! 💪"),
            ]
        },
        {
            "username": "photography_meera",
            "caption": "Golden Hour magic in the streets! Captured this raw portrait right as the sun hit 45 degrees. Camera settings: ISO 100, f/1.8, 1/500s 📸✨ #photography #goldenhour #streetphotography #portrait @art_by_sana",
            "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=800&auto=format&fit=crop&q=80",
            "filename": "post_photography_goldenhour.jpg",
            "comments": [
                ("design_with_riya", "The depth of field and warm tones are stunning Meera! 😍"),
                ("travel_with_anaya", "Golden hour shots are always my favorite."),
            ]
        },
        {
            "username": "code_with_rohan",
            "caption": "Clean code is not written by following set rules, but by caring about the craft and future developers reading it ☕🚀 #cleancode #python #devcommunity @nexora_dev",
            "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&auto=format&fit=crop&q=80",
            "filename": "post_code_rohan.jpg",
            "comments": [
                ("nexora_dev", "100% agreed! Readability over clever tricks every time."),
                ("music_arjun", "Coding with lo-fi beats in the background is the ultimate flow state 🎧"),
            ]
        },
        {
            "username": "tech_aarav",
            "caption": "Testing the latest ultra-wide curved monitor setup! 144Hz refresh rate and 99% DCI-P3 color accuracy is a dream for developers and designers alike 🚀💻 #techreview #desksetup #developer @nexora_dev",
            "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",
            "filename": "post_tech_desksetup.jpg",
            "comments": [
                ("design_with_riya", "That screen real estate looks amazing for Figma + code side by side!"),
                ("nexora_dev", "Desk setup goal right there 💻"),
            ]
        },
        {
            "username": "fitness_kabir",
            "caption": "Consistency beats intensity every single time! 5 AM workout done. Stay disciplined and focus on incremental daily progress 💪🏋️‍♂️ #fitness #workout #discipline #healthylifestyle @travel_with_anaya",
            "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&auto=format&fit=crop&q=80",
            "filename": "post_fitness_kabir.jpg",
            "comments": [
                ("travel_with_anaya", "Needed this Monday morning motivation! 🙌"),
                ("nexora_creator", "Discipline in fitness spills over into creative work too! 🔥"),
            ]
        },
        {
            "username": "art_by_sana",
            "caption": "New pastel canvas illustration completed today! Exploring soft color palettes and fluid organic shapes 🎨💖 #digitalart #illustration #artist #pastel @design_with_riya",
            "image_url": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=800&auto=format&fit=crop&q=80",
            "filename": "post_art_sana.jpg",
            "comments": [
                ("design_with_riya", "The color harmony here is breathtaking Sana! ✨"),
                ("photography_meera", "Framing and balance are perfect."),
            ]
        },
        {
            "username": "music_arjun",
            "caption": "In the studio working on a new chill lo-fi beat track for late night coding sessions 🎧🎹 Synthesizer melodies + vinyl warmth = pure focus mode! #lofi #musicproduction #studio #synth @tech_aarav",
            "image_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=800&auto=format&fit=crop&q=80",
            "filename": "post_music_arjun.jpg",
            "comments": [
                ("code_with_rohan", "Can't wait to add this track to my coding playlist! 🎧"),
                ("tech_aarav", "Lo-fi synth tracks hit different late at night!"),
            ]
        },
        {
            "username": "nexora_creator",
            "caption": "Connecting creators, engineers, designers, and artists from around the world on Nexora! 🌟 Building a positive and vibrant community. Thank you all for being part of this journey! #nexora #community #creators @design_with_riya @nexora_dev",
            "image_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&auto=format&fit=crop&q=80",
            "filename": "post_nexora_community.jpg",
            "comments": [
                ("design_with_riya", "Proud to design for this community! ❤️"),
                ("nexora_dev", "Excited for what's coming next on Nexora! 🚀"),
                ("travel_with_anaya", "Best community platform ever! ✨"),
            ]
        },
        {
            "username": "design_with_riya",
            "caption": "Diving deep into micro-animations & smooth transitions today. A well-placed 300ms cubic-bezier curve elevates the entire UX! 💫 #design #microinteractions #uidesign @nexora_creator",
            "image_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800&auto=format&fit=crop&q=80",
            "filename": "post_design_microinteractions.jpg",
            "comments": [
                ("art_by_sana", "Micro-animations make interfaces feel so alive! ✨"),
                ("nexora_dev", "Clean CSS transitions are pure joy to implement."),
            ]
        },
        {
            "username": "nexora_dev",
            "caption": "Configured asynchronous background tasks and cron schedules in Django! Zero blockages on the main thread means buttery smooth responses for users ⚡ #django #async #backend #python",
            "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80",
            "filename": "post_dev_async.jpg",
            "comments": [
                ("code_with_rohan", "Background task queues are essential for scalable web apps! 🚀"),
                ("tech_aarav", "Super fast response time! 🔥"),
            ]
        },
        {
            "username": "travel_with_anaya",
            "caption": "Chasing foggy morning coffee in the tea gardens of Munnar 🌿☕ The peaceful quiet before sunrise is pure bliss. #travel #munnar #teagardens #nature",
            "image_url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&auto=format&fit=crop&q=80",
            "filename": "post_travel_munnar.jpg",
            "comments": [
                ("photography_meera", "That morning fog lighting is dreamy! 🌿"),
                ("music_arjun", "Perfect atmosphere for listening to ambient lo-fi 🎧"),
            ]
        },
        {
            "username": "photography_meera",
            "caption": "Urban geometric symmetry! Architectural photography is all about finding harmony in lines, shadows, and perspective 🏛️✨ #photography #architecture #symmetry",
            "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop&q=80",
            "filename": "post_photo_architecture.jpg",
            "comments": [
                ("design_with_riya", "The grid alignment in this photo is perfection! 📐"),
                ("art_by_sana", "Architectural shadows are art in themselves."),
            ]
        },
        {
            "username": "tech_aarav",
            "caption": "Full desk tour video is live! Mechanical keyboard with custom linear switches + ergonomic setup = productivity unlocked ⌨️🚀 #tech #workspace #desksetup",
            "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
            "filename": "post_tech_keyboard.jpg",
            "comments": [
                ("nexora_dev", "Custom mechanical switches hit different! ⌨️"),
                ("code_with_rohan", "Checking out the review video right now."),
            ]
        },
        {
            "username": "fitness_kabir",
            "caption": "Nutrition tip: Fueling your body with whole foods and staying hydrated is 80% of the fitness journey. Keep it simple and stay consistent! 🥗💧 #fitness #nutrition #wellness",
            "image_url": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&auto=format&fit=crop&q=80",
            "filename": "post_fitness_nutrition.jpg",
            "comments": [
                ("travel_with_anaya", "Healthy fuel makes long travel days so much easier! 🥗"),
                ("nexora_creator", "Great advice Kabir! 🙌"),
            ]
        },
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting professional posts creation..."))

        posts_dir = os.path.join(settings.MEDIA_ROOT, "posts")
        os.makedirs(posts_dir, exist_ok=True)

        all_users = {u.username: u for u in User.objects.all()}
        created_posts_count = 0

        for data in self.PROFESSIONAL_POSTS:
            author = all_users.get(data["username"])
            if not author:
                self.stdout.write(self.style.WARNING(f"Author @{data['username']} not found, skipping post."))
                continue

            # Download post image
            img_filepath = os.path.join(posts_dir, data["filename"])
            if not os.path.exists(img_filepath):
                try:
                    req = urllib.request.Request(data["image_url"], headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response, open(img_filepath, 'wb') as out_file:
                        out_file.write(response.read())
                    self.stdout.write(self.style.SUCCESS(f"Downloaded image: {data['filename']}"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to download image {data['filename']}: {e}"))

            relative_img_path = f"posts/{data['filename']}" if os.path.exists(img_filepath) else None

            # Get or create post (avoid duplicate captions for same author)
            post, created = Post.objects.get_or_create(
                author=author,
                caption=data["caption"],
                defaults={
                    "image": relative_img_path
                }
            )

            if created:
                created_posts_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created post for @{author.username}"))

            # Add realistic likes from peer demo accounts
            other_users = [u for uname, u in all_users.items() if uname != author.username]
            for liker in other_users[:5]:  # Add 4-5 likes per post
                post.likes.add(liker)

            # Add professional peer comments
            for commenter_username, comment_text in data["comments"]:
                commenter = all_users.get(commenter_username)
                if commenter:
                    comment_obj, _ = Comment.objects.get_or_create(
                        post=post,
                        user=commenter,
                        text=comment_text
                    )
                    # Trigger notification for comment author
                    NotificationService.create_notification(
                        recipient=author,
                        sender=commenter,
                        notification_type="comment",
                        post=post
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully created {created_posts_count} professional feed posts with rich media, likes, and comments!"
            )
        )
