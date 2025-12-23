from django.urls import path
from . import views

app_name = "traveler"

urlpatterns = [
    path("dashboard/", views.traveler_dashboard_view, name="traveler_dashboard_view"),
    path("payment/start/",views.start_payment_view,name="start_payment_view"),
    path("payment/callback/",views.callback_view,name="callback_view"),
]
