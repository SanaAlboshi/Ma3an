from django.urls import path
from . import views

app_name = 'agency'  # هذا ضروري إذا تريد تستخدم namespace

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    #path('subscription/', views.subscription_view, name='subscription'),
    path('subscription/', views.subscription_view, name='subscription_view'),

    path('select-subscription/<int:subscription_id>/', views.select_subscription_view, name='select_subscription'),
    path('subscription/callback/', views.subscription_callback_view, name='subscription_callback'),
    
    path('add-tour/', views.add_tour_view, name='add_tour'),
    path('all-tours/', views.all_tours_view, name='all_tours'),
    path('tour/edit/<int:tour_id>/', views.edit_tour_view, name='edit_tour'),
    
    path('tour/delete/<int:tour_id>/', views.delete_tour_view, name='delete_tour'),
    path('tour/<int:tour_id>/', views.tour_detail_view, name='tour_detail'),
    # Payment
    path('subscription/payment/', views.agency_payment_view, name='agency_payment'),
    path('tour/<int:tour_id>/add-schedule/', views.add_schedule_view, name='add_schedule'),
    path('confirm-tour/<int:tour_id>/', views.confirm_tour_view, name='confirm_tour'),
    path('my_tours/', views.my_tours_view, name='my_tours'),



]
