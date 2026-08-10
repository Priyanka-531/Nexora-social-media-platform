# 🚀 Nexora — Social Media Platform

Nexora is a modern, responsive social media platform built with Django.  
It provides a social-media experience where users can create profiles, share posts, interact with other users, follow people, discover content, and communicate through social interactions.

The project combines a Django backend with a modern, professional UI designed for a smooth social-media experience.

---

## ✨ Features

### 🔐 Authentication
- User registration
- User login
- User logout
- Secure password handling
- Django authentication system

### 👤 User Profiles
- Custom user profiles
- Profile picture
- Cover picture
- Bio
- Location
- College
- Profession
- Website
- Edit profile
- Public profile viewing

### 🏠 Home Feed
- Dynamic social-media feed
- User posts
- Post images
- Captions
- Post timestamps
- Suggested users
- Stories section
- Feed categories

### 📝 Posts
- Create posts
- Upload images
- Add captions
- Display posts in the feed
- User-specific posts
- Profile post grid

### ❤️ Social Interactions
- Like / Unlike posts
- Like counts
- Comments
- Comment counts
- Follow / Unfollow
- Followers
- Following
- Follow requests

### 🔎 Search
- Search users
- Search usernames
- Search first names
- Search last names
- Search posts
- Search post captions
- Search results page
- User profile navigation

### 📸 Stories
- Story display
- Story profiles
- Story viewer
- Story images
- Story expiration support

### 🔔 Notifications
- Social interaction notifications
- Follow request notifications
- Follow notifications
- Like notifications
- Comment notifications
- Read/unread notification states

### 💡 User Discovery
- Suggested users
- Dummy/demo profiles for development
- Follow suggestions
- Profile discovery

### 📱 Responsive UI
- Desktop-friendly interface
- Tablet-friendly layout
- Mobile-friendly layout
- Responsive navigation
- Modern social-media cards

---

## 🛠️ Technologies Used

### Backend
- Python
- Django
- Django ORM
- SQLite

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap
- Font Awesome
- Google Stitch UI

### Development Tools
- Visual Studio Code
- Git
- GitHub

---

## 📂 Project Structure

```text
Nexora/
│
├── nexora/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── users/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── signals.py
│
├── posts/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── interactions/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── edit_profile.html
│   ├── create_post.html
│   └── search_results.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/
│   ├── profile_pictures/
│   ├── cover_pictures/
│   └── posts/
│
├── db.sqlite3
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
