from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class RegistrationForm(UserCreationForm):
    display_name = forms.CharField(max_length=80, required=True, help_text="How your name appears to other people.")
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "display_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        # Store display name in Django's first_name field for Phase 1.
        user.first_name = self.cleaned_data["display_name"].strip()
        if commit:
            user.save()
        return user
