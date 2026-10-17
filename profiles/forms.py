from django import forms
from django.contrib.auth import get_user_model
from .models import Profile, UserReport

User = get_user_model()

class ProfileEditForm(forms.ModelForm):
    display_name = forms.CharField(max_length=150, required=False, label="Display name")
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ("bio", "avatar", "is_private")
        widgets = {"bio": forms.Textarea(attrs={"rows": 4, "maxlength": 280, "placeholder": "A little about you…"})}
        labels = {"is_private": "Make my profile private"}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["display_name"].initial = self.user.first_name
        self.fields["email"].initial = self.user.email
        self.fields["avatar"].required = False

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("That email address is already in use.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data["display_name"].strip()
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save(update_fields=["first_name", "email"])
            profile.save()
        return profile

class UserReportForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ("reason", "details")
        widgets = {"details": forms.Textarea(attrs={"rows": 4, "maxlength": 1000, "placeholder": "Share details that may help our moderators (optional)."})}
