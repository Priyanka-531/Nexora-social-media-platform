from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


class RegisterForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({
                "class": "nx-form-control"
            })


class EditProfileForm(forms.ModelForm):

    class Meta:

        model = Profile

        fields = [
            "profile_picture",
            "cover_picture",
            "bio",
            "location",
            "college",
            "profession",
            "website",
        ]

        widgets = {

            "bio": forms.Textarea(attrs={
                "class": "nx-form-control",
                "rows": 4,
                "placeholder": "Write something about yourself..."
            }),

            "location": forms.TextInput(attrs={
                "class": "nx-form-control",
                "placeholder": "Your location"
            }),

            "college": forms.TextInput(attrs={
                "class": "nx-form-control",
                "placeholder": "College"
            }),

            "profession": forms.TextInput(attrs={
                "class": "nx-form-control",
                "placeholder": "Profession"
            }),

            "website": forms.URLInput(attrs={
                "class": "nx-form-control",
                "placeholder": "https://example.com"
            }),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["profile_picture"].widget.attrs.update({
            "class": "nx-form-control"
        })

        self.fields["cover_picture"].widget.attrs.update({
            "class": "nx-form-control"
        })