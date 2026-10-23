import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ProfileEditForm, UserReportForm
from .models import Profile, Follow, Block, UserReport, Notification
from config.firebase_db import firebase_reference
from home.firebase_users import publish_user

User = get_user_model()

@login_required
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "profiles/detail.html", {"profile_user": request.user, "profile": profile, "is_own_profile": True, "is_following": False, "is_blocked": False, "is_blocked_by": False, "can_view_profile": True})


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
        user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        profile = form.save()

        try:
            publish_user(request.user)

            firebase_reference(
                f"users/{request.user.pk}"
            ).update({
                "bio": profile.bio or "",
            })

        except Exception:
        
            logging.getLogger(__name__).exception(
                "Could not sync updated profile to Firebase."
            )

        messages.success(
            request,
            "Your .Vibez profile and privacy settings have been updated."
        )
        return redirect("my_profile")

    return render(
        request,
        "profiles/edit.html",
        {"form": form},
    )


@login_required
def public_profile(request, username):
    profile_user = get_object_or_404(User.objects.select_related("profile"), username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    own = profile_user.pk == request.user.pk
    is_blocked = Block.objects.filter(blocker=request.user, blocked=profile_user).exists()
    is_blocked_by = Block.objects.filter(blocker=profile_user, blocked=request.user).exists()
    is_following = Follow.objects.filter(follower=request.user, followed=profile_user).exists()
    can_view_profile = own or not profile.is_private or is_following
    if is_blocked or is_blocked_by:
        can_view_profile = own
    return render(request, "profiles/detail.html", {
        "profile_user": profile_user, "profile": profile, "is_own_profile": own,
        "is_following": is_following, "is_blocked": is_blocked,
        "is_blocked_by": is_blocked_by, "can_view_profile": can_view_profile,
    })

@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target.pk == request.user.pk:
        messages.error(request, "You cannot follow yourself.")
        return redirect("public_profile", username=username)
    if Block.objects.filter(blocker=request.user, blocked=target).exists() or Block.objects.filter(blocker=target, blocked=request.user).exists():
        messages.error(request, "You cannot follow this account.")
        return redirect("public_profile", username=username)
    relation = Follow.objects.filter(follower=request.user, followed=target)
    if relation.exists():
        relation.delete()
        messages.success(request, f"You unfollowed {target.username}.")
    else:
        try:
            Follow.objects.create(follower=request.user, followed=target)
            Notification.objects.create(recipient=target, actor=request.user, kind="follow", message=f"{request.user.username} started following you.", target_url=f"/profiles/{request.user.username}/")
            messages.success(request, f"You are now following {target.username}.")
        except IntegrityError:
            pass
    return redirect("public_profile", username=username)

@login_required
@require_POST
def toggle_block(request, username):
    target = get_object_or_404(User, username=username)
    if target.pk == request.user.pk:
        messages.error(request, "You cannot block yourself.")
        return redirect("my_profile")
    existing = Block.objects.filter(blocker=request.user, blocked=target)
    if existing.exists():
        existing.delete()
        messages.success(request, f"You unblocked {target.username}.")
    else:
        Block.objects.get_or_create(blocker=request.user, blocked=target)
        messages.success(request, f"You blocked {target.username}. Their follow relationship with you was removed.")
    return redirect("public_profile", username=username)

@login_required
@require_POST
def report_user(request, username):
    target = get_object_or_404(User, username=username)
    if target.pk == request.user.pk:
        messages.error(request, "You cannot report your own account.")
        return redirect("my_profile")
    if UserReport.objects.filter(reporter=request.user, reported_user=target, reviewed=False).exists():
        messages.info(request, "You already submitted a report about this account that is awaiting review.")
        return redirect("public_profile", username=username)
    form = UserReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.reported_user = target
        report.save()
        messages.success(request, "Thanks. Your report was sent to the .Vibez moderation team.")
    else:
        messages.error(request, "Please choose a valid report reason.")
    return redirect("public_profile", username=username)

@login_required
def notifications_view(request):
    notifications = request.user.notifications.select_related("actor")[:100]
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "profiles/notifications.html", {"notifications": notifications})
