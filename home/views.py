from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from profiles.models import Follow, Block
from .forms import RoomForm
from .models import Room, RoomMembership

User = get_user_model()
SEAT_COUNT = 8


def unique_open_rooms():
    """Return one open room per host/title, keeping the newest duplicate."""
    queryset = Room.objects.filter(status=Room.Status.OPEN).select_related("host").order_by("-created_at", "-pk")
    seen = set()
    unique_rooms = []
    for room in queryset:
        key = (room.host_id, " ".join(room.title.casefold().split()))
        if key in seen:
            continue
        seen.add(key)
        unique_rooms.append(room)
    return unique_rooms


def home_view(request):
    rooms = unique_open_rooms()[:3]
    return render(request, "home/index.html", {"live_rooms": rooms})


def discover_view(request):
    query = request.GET.get("q", "").strip()[:80]
    users = User.objects.exclude(pk=request.user.pk) if request.user.is_authenticated else User.objects.all()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(first_name__icontains=query))
    if request.user.is_authenticated:
        followed_ids = Follow.objects.filter(follower=request.user).values_list("followed_id", flat=True)
        blocked_ids = Block.objects.filter(blocker=request.user).values_list("blocked_id", flat=True)
        blocked_by_ids = Block.objects.filter(blocked=request.user).values_list("blocker_id", flat=True)
        users = users.exclude(pk__in=followed_ids).exclude(pk__in=blocked_ids).exclude(pk__in=blocked_by_ids)
    users = users.order_by("username").distinct()[:60]
    return render(request, "home/discover.html", {"people": users, "query": query})


def rooms_view(request):
    rooms = unique_open_rooms()
    return render(request, "home/rooms.html", {"rooms": rooms})


@login_required
def create_room(request):
    form = RoomForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        room = form.save(commit=False)
        room.host = request.user
        normalized_title = " ".join(room.title.casefold().split())
        existing_room = next((
            candidate for candidate in Room.objects.filter(
                host=request.user, status=Room.Status.OPEN
            ).order_by("-created_at", "-pk")
            if " ".join(candidate.title.casefold().split()) == normalized_title
        ), None)
        if existing_room:
            messages.info(request, "You already have an open room with this title. We opened your existing room instead.")
            return redirect("room_detail", room_id=existing_room.pk)
        room.save()
        RoomMembership.objects.get_or_create(
            room=room,
            user=request.user,
            defaults={"role": RoomMembership.Role.HOST},
        )
        messages.success(request, "Your room is live. Invite people to join the conversation!")
        return redirect("room_detail", room_id=room.pk)
    return render(request, "home/room_form.html", {"form": form})


def room_detail(request, room_id):
    room = get_object_or_404(Room.objects.select_related("host"), pk=room_id)
    membership = (
        room.memberships.filter(user=request.user).first()
        if request.user.is_authenticated else None
    )
    members = room.memberships.select_related("user").order_by("joined_at")
    seated_members = {
        member.seat_number: member
        for member in members
        if member.seat_number is not None and 1 <= member.seat_number <= SEAT_COUNT
    }
    seats = [
        {"number": number, "member": seated_members.get(number)}
        for number in range(1, SEAT_COUNT + 1)
    ]
    return render(request, "home/room_detail.html", {
        "room": room,
        "is_member": membership is not None,
        "membership": membership,
        "members": members,
        "seats": seats,
        "seat_count": SEAT_COUNT,
        "occupied_seat_count": len(seated_members),
        "is_host": request.user.is_authenticated and room.host_id == request.user.id,
    })


@login_required
@require_POST
def join_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id, status=Room.Status.OPEN)
    if room.host_id == request.user.id:
        RoomMembership.objects.get_or_create(
            room=room, user=request.user,
            defaults={"role": RoomMembership.Role.HOST},
        )
        messages.info(request, "You're the host of this room already.")
    else:
        RoomMembership.objects.get_or_create(room=room, user=request.user)
        messages.success(request, f"You're in {room.title}! You can listen or take an open seat.")
    return redirect("room_detail", room_id=room.pk)


@login_required
@require_POST
def leave_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    RoomMembership.objects.filter(room=room, user=request.user).delete()
    messages.success(request, f"You left {room.title}.")
    return redirect("room_detail", room_id=room.pk)


@login_required
@require_POST
def join_seat(request, room_id, seat_number):
    room = get_object_or_404(Room, pk=room_id, status=Room.Status.OPEN)
    if not 1 <= seat_number <= SEAT_COUNT:
        messages.error(request, "That seat does not exist.")
        return redirect("room_detail", room_id=room.pk)

    try:
        with transaction.atomic():
            # Lock the room row where supported, then check the seat and assign it.
            Room.objects.select_for_update().get(pk=room.pk)
            membership, _ = RoomMembership.objects.get_or_create(
                room=room,
                user=request.user,
                defaults={
                    "role": RoomMembership.Role.HOST if room.host_id == request.user.id
                    else RoomMembership.Role.LISTENER
                },
            )
            occupied = RoomMembership.objects.filter(
                room=room, seat_number=seat_number
            ).exclude(pk=membership.pk).exists()
            if occupied:
                messages.error(request, "That seat is already occupied. Choose another seat.")
                return redirect("room_detail", room_id=room.pk)

            membership.seat_number = seat_number
            membership.role = (
                RoomMembership.Role.HOST if room.host_id == request.user.id
                else RoomMembership.Role.SPEAKER
            )
            membership.save(update_fields=["seat_number", "role"])
    except IntegrityError:
        messages.error(request, "That seat was just taken. Please choose another.")
        return redirect("room_detail", room_id=room.pk)

    messages.success(request, f"You're now in Seat {seat_number}.")
    return redirect("room_detail", room_id=room.pk)


@login_required
@require_POST
def leave_seat(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    membership = get_object_or_404(RoomMembership, room=room, user=request.user)
    if membership.seat_number is None:
        messages.info(request, "You're not occupying a talking seat.")
    else:
        old_seat = membership.seat_number
        membership.seat_number = None
        membership.is_muted = False
        membership.role = (
            RoomMembership.Role.HOST if room.host_id == request.user.id
            else RoomMembership.Role.LISTENER
        )
        membership.save(update_fields=["seat_number", "is_muted", "role"])
        messages.success(request, f"You left Seat {old_seat}.")
    return redirect("room_detail", room_id=room.pk)


@login_required
@require_POST
def close_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id, host=request.user)
    room.status = Room.Status.CLOSED
    room.save(update_fields=["status", "updated_at"])
    messages.success(request, "Room closed. Members can no longer join.")
    return redirect("room_detail", room_id=room.pk)


@login_required
@require_POST
def reopen_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id, host=request.user)
    room.status = Room.Status.OPEN
    room.save(update_fields=["status", "updated_at"])
    messages.success(request, "Room reopened.")
    return redirect("room_detail", room_id=room.pk)


@login_required
@require_POST
def set_member_role(request, room_id, user_id):
    room = get_object_or_404(Room, pk=room_id, host=request.user)
    membership = get_object_or_404(RoomMembership, room=room, user_id=user_id)
    role = request.POST.get("role")

    if membership.user_id == room.host_id:
        messages.error(request, "The host role cannot be changed here.")
    elif role == RoomMembership.Role.SPEAKER:
        occupied = set(
            RoomMembership.objects.filter(room=room, seat_number__isnull=False)
            .exclude(pk=membership.pk)
            .values_list("seat_number", flat=True)
        )
        free_seat = next((n for n in range(1, SEAT_COUNT + 1) if n not in occupied), None)
        if free_seat is None:
            messages.error(request, "All eight talking seats are occupied.")
        else:
            membership.seat_number = free_seat
            membership.role = RoomMembership.Role.SPEAKER
            membership.save(update_fields=["seat_number", "role"])
            messages.success(request, f"{membership.user.username} is now in Seat {free_seat}.")
    elif role == RoomMembership.Role.LISTENER:
        membership.seat_number = None
        membership.role = RoomMembership.Role.LISTENER
        membership.save(update_fields=["seat_number", "role"])
        messages.success(request, f"{membership.user.username} is now a listener.")
    else:
        messages.error(request, "Invalid room role.")
    return redirect("room_detail", room_id=room.pk)


@login_required
@require_POST
def toggle_member_mute(request, room_id, user_id):
    room = get_object_or_404(Room, pk=room_id, host=request.user)
    membership = get_object_or_404(RoomMembership, room=room, user_id=user_id)
    if membership.user_id == room.host_id:
        messages.error(request, "The host cannot be muted from this control.")
    elif membership.seat_number is None:
        messages.error(request, "Only a seated speaker can be muted.")
    else:
        membership.is_muted = not membership.is_muted
        membership.save(update_fields=["is_muted"])
        messages.success(request, f"Mute setting updated for {membership.user.username}.")
    return redirect("room_detail", room_id=room.pk)


@login_required
def agora_token_view(request, room_id):
    """Issue a short-lived Agora RTC token to a member of this room."""
    import json
    import os
    import time
    from django.http import JsonResponse

    room = get_object_or_404(Room, pk=room_id)
    membership = get_object_or_404(RoomMembership, room=room, user=request.user)
    app_id = os.environ.get("AGORA_APP_ID", "").strip()
    app_certificate = os.environ.get("AGORA_APP_CERTIFICATE", "").strip()
    if not app_id or not app_certificate:
        return JsonResponse({"error": "Agora is not configured. Set AGORA_APP_ID and AGORA_APP_CERTIFICATE in your .env file."}, status=503)
    if room.status != Room.Status.OPEN:
        return JsonResponse({"error": "This room is closed."}, status=403)

    can_publish = membership.seat_number is not None and not membership.is_muted
    try:
        from agora_token_builder import RtcTokenBuilder, Role_Publisher, Role_Subscriber
    except ImportError:
        return JsonResponse({"error": "Agora token package missing. Run: pip install agora-token-builder"}, status=503)

    uid = int(request.user.pk)
    channel_name = f"vibez_room_{room.pk}"
    expiry = int(time.time()) + 3600
    role = Role_Publisher if can_publish else Role_Subscriber
    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, role, expiry
    )
    return JsonResponse({
        "appId": app_id, "channelName": channel_name, "token": token,
        "uid": uid, "canPublish": can_publish, "isMuted": membership.is_muted,
        "expiresAt": expiry,
    })
