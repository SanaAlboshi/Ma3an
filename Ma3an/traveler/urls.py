from django.urls import path
from . import views

app_name = "traveler"

urlpatterns = [
    path("dashboard/", views.traveler_dashboard, name="dashboard"),
    path("tours/", views.all_tours, name="all_tours"),
    path("tours/<int:tour_id>/", views.tour_detail, name="tour_detail"),
    path("payment/<int:tour_id>/", views.payment_view, name="payment"),
]
