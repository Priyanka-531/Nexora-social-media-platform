from django import forms

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:

        model = Post

        fields = [
            "image",
            "caption"
        ]

        widgets = {

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "nx-form-control",
                    "accept": "image/*"
                }
            ),

            "caption": forms.Textarea(
                attrs={
                    "class": "nx-form-control",
                    "rows": 4,
                    "placeholder": "What's happening today?"
                }
            ),
        }