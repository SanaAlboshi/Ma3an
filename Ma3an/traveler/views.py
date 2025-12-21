import stripe
import json
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.urls import reverse
from django.db import transaction
from django.db.models import Q
from accounts.models import Traveler, Notification
from traveler.models import TravelerPayment, TravelerLocation
from agency.models import Tour, TourSchedule
from traveler.services.active_tour import get_active_join
from traveler.services.location_service import save_traveler_location
from traveler.services.geofence_service import check_geofences_and_notify_users

stripe.api_key = settings.STRIPE_SECRET_KEY

def traveler_dashboard_view(request):
    traveler = Traveler.objects.get(user=request.user)
    active_tours = TravelerPayment.objects.filter(traveler=traveler, status="paid")

    user = request.user

    notifications = Notification.objects.filter(
        user=user
    ).order_by("-created_at")[:10]

    # announcements = Announcement.objects.filter(tour__in=[t.tour for t in active_tours])
    next_event = TourSchedule.objects.filter(
        tour__in=[t.tour for t in active_tours]
    ).order_by("event_date").first()

    return render(request, "traveler/traveler_dashboard.html", {
        "active_tours": active_tours,
        "notifications": notifications,
        "next_event": next_event,
    })


def tours_view(request):
    query = request.GET.get("q", "")
    tours = Tour.objects.filter(
        Q(tour_name__icontains=query) |
        Q(travel_agency__agencyName__icontains=query)
    )
    return render(request, "traveler/tours_view.html", {"tours": tours})

def tour_detail_view(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    traveler = Traveler.objects.get(user=request.user)

    joined = TravelerPayment.objects.filter(traveler=traveler, tour=tour, status="paid").exists()

    if request.method == "POST" and not joined:
        TravelerPayment.objects.create(
            traveler=traveler,
            tour=tour,
            amount=tour.price
        )
        return redirect("traveler:payment", tour_id=tour.id)

    return render(request, "traveler/tour_detail.html", {
        "tour": tour,
        "joined": joined
    })


def traveler_payment_view(request, tour_id):
    traveler = Traveler.objects.get(user=request.user)
    join = get_object_or_404(TravelerPayment, traveler=traveler, tour_id=tour_id)

    intent = stripe.PaymentIntent.create(
        amount=int(join.amount * 100),  # cents
        currency="usd",
        metadata={"tour_id": tour_id, "traveler": traveler.id},
    )

    return render(request, "traveler/payment.html", {
        "client_secret": intent.client_secret,
        "stripe_key": settings.STRIPE_PUBLISHABLE_KEY,
        "join": join
    })

def payment_success(request, tour_id):
    join = get_object_or_404(TravelerPayment, tour_id=tour_id, traveler__user=request.user)
    join.status = "paid"
    join.save()
    messages.success(request, "Payment successful 🎉")
    return redirect("traveler:tour_detail_view", tour_id=tour_id)


@login_required
def save_location_view(request):
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    data = json.loads(request.body)
    lat = data.get("lat")
    lng = data.get("lng")
    accuracy = data.get("accuracy")

    if not lat or not lng:
        return JsonResponse({"ok": False}, status=400)

    traveler = request.user.traveler



    active_join = get_active_join(traveler)
    if not active_join:
        return JsonResponse({"ok": False, "error": "No active tour"}, status=403)

    current_location = save_traveler_location(
        traveler,
        active_join.tour,
        lat,
        lng,
        accuracy
    )

    alerts = check_geofences_and_notify_users(
        current_location=current_location,
        traveler=traveler,
        tour=active_join.tour
    )

    for alert in alerts:
        print("Notify traveler & tour guide")

    return JsonResponse({"ok": True})

def traveler_required(view_func):
    return user_passes_test(lambda u: hasattr(u, "traveler"))(view_func)