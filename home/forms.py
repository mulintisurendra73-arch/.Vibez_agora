from django import forms
from .models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["title", "description", "topic"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "e.g. Late night thoughts",
                "maxlength": 80,
            }),
            "description": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "What would you like to talk about?",
            }),
            "topic": forms.TextInput(attrs={
                "placeholder": "Music, wellness, gaming…",
                "maxlength": 40,
            }),
        }
