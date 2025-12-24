import json
import requests
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.urls import reverse
from django.db import transaction
from django.db.models import Q
from accounts.models import Traveler, Notification
from traveler.models import Review,TravelerPayment, TravelerLocation
from agency.models import Tour, TourSchedule
from traveler.services.active_tour import get_active_join
from traveler.services.location_service import save_traveler_location
from traveler.services.geofence_service import check_geofences_and_notify_users, is_inside_geofence
from django.views.decorators.csrf import csrf_exempt
from agency.models import Geofence, GeofenceEvent



def traveler_dashboard_view(request):
    traveler = request.user.traveler_profile

    # Paid tours
    payments = (
        TravelerPayment.objects
        .filter(traveler=traveler, status=TravelerPayment.Status.PAID)
        .select_related("tour")
    )

    tours_data = []

    for payment in payments:
        tour = payment.tour

        next_event = (
            TourSchedule.objects
            .filter(tour=tour)
            .order_by("day_number", "start_time")
            .first()
        )

        review = Review.objects.filter(traveler=traveler, tour=tour).first()

        tours_data.append({
            "tour": tour,
            "next_event": next_event,
            "review": review,
        })

    # Geofence notifications
    notifications = (
        Notification.objects
        .filter(user=request.user)
        .select_related("event", "event__geofence")
        .order_by("-created_at")[:10]
    )

    # Save rivew
    if request.method == "POST":
        tour_id = request.POST.get("tour_id")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        tour = get_object_or_404(Tour, id=tour_id)

        Review.objects.update_or_create(
            traveler=traveler,
            tour=tour,
            defaults={
                "rating": rating,
                "comment": comment
            }
        )
        return redirect("traveler:traveler_dashboard_view")

    return render(request, "traveler/traveler_dashboard.html", {
        "tours_data": tours_data,
        "notifications": notifications,
    })



def traveler_tour_detail_view(request, tour_id):
    tour = get_object_or_404(
        Tour.objects.select_related(
            "agency",
            "tour_guide",
            "tour_guide__user"
        ).prefetch_related(
            "schedules"
        ),
        id=tour_id
    )

    schedules = tour.schedules.all().order_by("day_number", "start_time")

    return render(request, "traveler/tour_details.html", {
        "tour": tour,
        "schedules": schedules,
    })



def start_payment_view(request):
    tour = get_object_or_404(Tour, id=request.GET.get("tour_id"))

    # Is the flight full?
    paid_count = TravelerPayment.objects.filter(
        tour=tour,
        status=TravelerPayment.Status.PAID
    ).count()

    if tour.travelers and paid_count >= tour.travelers:
        messages.error(request, "This tour is fully booked.")
        return redirect("agency:all_tours")

    # Did she/he prepaid?
    already_paid = TravelerPayment.objects.filter(
        traveler=request.user.traveler_profile,
        tour=tour,
        status=TravelerPayment.Status.PAID
    ).exists()

    if already_paid:
        messages.warning(request, "You already paid for this tour.")
        return redirect("agency:all_tours")

    # Open the payment page
    return render(request, "traveler/payment_checkout.html", {
        "tour": tour,
        "amount": int(tour.price * 100),
        "display_price": tour.price, 
        "publishable_key": settings.MOYASAR_PUBLISHABLE_KEY,
        "callback_url": request.build_absolute_uri(
            reverse("traveler:callback_view")
        ),
    })


def callback_view(request):
    moyasar_id = request.GET.get("id")

    if not moyasar_id:
        return render(request, "traveler/payment_result.html", {
            "success": False,
            "message": "Missing payment id"
        })

    # Ask Moyasar about the payment result
    r = requests.get(
        f"{settings.MOYASAR_BASE_URL}/payments/{moyasar_id}",
        auth=(settings.MOYASAR_SECRET_KEY, ""),
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    status = data.get("status")
    metadata = data.get("metadata", {})

    tour_id = metadata.get("tour_id")
    user_id = metadata.get("user_id")

    if not tour_id or not user_id:
        return render(request, "traveler/payment_result.html", {
            "success": False,
            "message": "Invalid payment metadata"
        })

    traveler = Traveler.objects.get(user_id=user_id)
    tour = Tour.objects.get(id=tour_id)

    # Update the database
    with transaction.atomic():
        payment, _ = TravelerPayment.objects.get_or_create(
            moyasar_id=moyasar_id,
            defaults={
                "traveler": traveler,
                "tour": tour,
                "amount": data["amount"],
                "currency": data["currency"],
                "description": data.get("description", ""),
            }
        )

        payment.raw = data

        if status == "paid":
            payment.status = TravelerPayment.Status.PAID
        elif status in ["failed", "canceled"]:
            payment.status = TravelerPayment.Status.FAILED
        else:
            payment.status = TravelerPayment.Status.INITIATED

        payment.save()

    return render(request, "traveler/payment_result.html", {
        "success": status == "paid",
        "payment": payment
    })




@csrf_exempt
def save_traveler_location(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    traveler = request.user.traveler_profile
    lat = float(request.POST.get("latitude"))
    lng = float(request.POST.get("longitude"))
    tour_id = request.POST.get("tour_id")
    tour_id = request.POST.get("tour_id")

    if not tour_id:
        return JsonResponse(
            {"error": "tour_id is required"},
            status=400
        )


    geofences = Geofence.objects.filter(
        schedule__tour_id=tour_id,
        is_active=True
    ).select_related("schedule", "schedule__tour", "schedule__tour__tour_guide")

    results = []

    for geofence in geofences:
        schedule = geofence.schedule

        if not schedule.latitude or not schedule.longitude:
            continue

        inside, distance = is_inside_geofence(
            lat,
            lng,
            float(schedule.latitude),
            float(schedule.longitude),
            geofence.radius_meters
        )

        tour_guide = schedule.tour.tour_guide


        last_event = GeofenceEvent.objects.filter(
            traveler=traveler,
            geofence=geofence
        ).order_by("-occurred_at").first()

        if (
            not inside
            and geofence.trigger_on_exit
            and (not last_event or last_event.event_type != "exit")
        ):
            GeofenceEvent.objects.create(
                traveler=traveler,
                tour_guide=tour_guide,
                geofence=geofence,
                event_type="exit"
            )

            # Notification traveler
            Notification.objects.create(
                user=traveler.user,
                title="⚠️ You left the allowed area",
                message=f"You moved away from {schedule.activity_title}"
            )

            # Notification tour guide
            if tour_guide:
                Notification.objects.create(
                    user=tour_guide.user,
                    title="🚨 Traveler left geofence",
                    message=f"{traveler.user.username} left {schedule.activity_title}"
                )

            results.append("exit")

        # 🟢 ENTER
        if (
            inside
            and geofence.trigger_on_enter
            and last_event
            and last_event.event_type == "exit"
        ):
            GeofenceEvent.objects.create(
                traveler=traveler,
                tour_guide=tour_guide,
                geofence=geofence,
                event_type="enter"
            )

            results.append("enter")
    print("POST DATA:", request.POST)
    return JsonResponse({
        "status": "ok",
        "events": results
    })
