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
from traveler.models import TravelerPayment, TravelerLocation
from agency.models import Tour, TourSchedule
from traveler.services.active_tour import get_active_join
from traveler.services.location_service import save_traveler_location
from traveler.services.geofence_service import check_geofences_and_notify_users



def traveler_dashboard_view(request):
    traveler = Traveler.objects.get(user=request.user)
    active_tours = TravelerPayment.objects.filter(traveler=traveler, status="paid")

    user = request.user

    notifications = Notification.objects.filter(
        user=user
    ).order_by("-created_at")[:10]

    # # announcements = Announcement.objects.filter(tour__in=[t.tour for t in active_tours])
    # next_event = TourSchedule.objects.filter(
    #     tour__in=[t.tour for t in active_tours]
    # ).order_by("event_date").first()

    return render(request, "traveler/traveler_dashboard.html", {
        "active_tours": active_tours,
        "notifications": notifications,
        # "next_event": next_event,
    })


# def tour_detail_view(request, tour_id):
#     tour = get_object_or_404(Tour, id=tour_id)
#     traveler = Traveler.objects.get(user=request.user)

#     joined = TravelerPayment.objects.filter(traveler=traveler, tour=tour, status="paid").exists()

#     if request.method == "POST" and not joined:
#         TravelerPayment.objects.create(
#             traveler=traveler,
#             tour=tour,
#             amount=tour.price
#         )
#         return redirect("traveler:payment", tour_id=tour.id)

#     return render(request, "traveler/tour_detail.html", {
#         "tour": tour,
#         "joined": joined
#     })



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
        return redirect("traveler:traveler_dashboard_view")

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