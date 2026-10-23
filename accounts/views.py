from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import RegistrationForm
from home.firebase_users import publish_user

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegistrationForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
      user = form.save()

      try:
        publish_user(user)
      except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Could not sync the new user to Firebase."
        )

    messages.success(
        request,
        "Your account is ready. You can sign in now."
    )
    return redirect("login")

    return render(request, "accounts/register.html", {"form": form})
