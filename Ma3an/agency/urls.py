from django.urls import path
from . import views

app_name = 'agency'  # هذا ضروري إذا تريد تستخدم namespace

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('subscription/', views.subscription_view, name='subscription'),
    path('add-tour/', views.add_tour_view, name='add_tour'),
    path('all-tours/', views.all_tours_view, name='all_tours'),
    path('tour/edit/<int:tour_id>/', views.edit_tour_view, name='edit_tour'),
    path('tour/delete/<int:tour_id>/', views.delete_tour_view, name='delete_tour'),
    path('tour/<int:tour_id>/', views.tour_detail_view, name='tour_detail'),
    # Payment
    path('subscription/payment/', views.agency_payment_view, name='agency_payment'),
    path('tour/<int:tour_id>/add-schedule/', views.add_schedule_view, name='add_schedule'),
    path('profile/', views.agency_profile, name='agency_profile'),


]
