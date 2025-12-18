from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Traveler, TourJoin
import random
# from tours.models import Tour

def traveler_dashboard(request):
    traveler = Traveler.objects.get(user=request.user)
    active_tours = TourJoin.objects.filter(traveler=traveler, status="paid")

    return render(request, "traveler/traveler_dashboard.html", {
        "active_tours": active_tours,
    })


def all_tours(request):
    query = request.GET.get("q", "")
    tours = Tour.objects.filter(
        Q(tour_name__icontains=query) |
        Q(travel_agency__agencyName__icontains=query)
    )
    return render(request, "traveler/all_tours.html", {"tours": tours})

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    traveler = Traveler.objects.get(user=request.user)

    joined = TourJoin.objects.filter(traveler=traveler, tour=tour, status="paid").exists()

    if request.method == "POST" and not joined:
        TourJoin.objects.create(
            traveler=traveler,
            tour=tour,
            amount=tour.price
        )
        return redirect("traveler:payment", tour_id=tour.id)

    return render(request, "traveler/tour_detail.html", {
        "tour": tour,
        "joined": joined
    })


def payment_view(request, tour_id):
    traveler = Traveler.objects.get(user=request.user)
    join = get_object_or_404(TourJoin, traveler=traveler, tour_id=tour_id)

    if request.method == "POST":
        success = random.choice([True, False])  # simulation

        if success:
            join.status = "paid"
            join.save()
            messages.success(request, "Payment successful 🎉")
            return redirect("traveler:tour_detail", tour_id=tour_id)
        else:
            join.status = "failed"
            join.save()
            messages.error(request, "Payment failed ❌ Please try again.")

    return render(request, "traveler/payment.html", {"join": join})


def traveler_dashboard(request):
    traveler = Traveler.objects.get(user=request.user)
    active_tours = TourJoin.objects.filter(traveler=traveler, status="paid")

    return render(request, "traveler/traveler_dashboard.html", {
        "active_tours": active_tours,
    })
