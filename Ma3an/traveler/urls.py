from django.urls import path
from . import views

app_name = "traveler"

urlpatterns = [
    path("dashboard/", views.traveler_dashboard_view, name="traveler_dashboard_view"),
    path("tour/detail/<int:tour_id>/", views.traveler_tour_detail_view, name="traveler_tour_detail_view"),
    path("payment/start/",views.start_payment_view,name="start_payment_view"),
    path("payment/callback/",views.callback_view,name="callback_view"),
    path("save-location/", views.save_traveler_location, name="save_location"),
]
