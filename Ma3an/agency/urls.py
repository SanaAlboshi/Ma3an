# agency/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('subscription/', views.subscription_view, name='subscription'),
    path('add-tour/', views.add_tour_view, name='add_tour'),
    path('all-tours/', views.all_tours_view, name='all_tours'),
    path('save-tour/', views.save_tour_view, name='save_tour'),

    # TourGuide URLs
    path('add_tour_guide/', views.add_tour_guide_view, name='add_tour_guide'),
    path('all_tour_guides/', views.all_tour_guides_view, name='all_tour_guides'),

    # Tour management
    path('tour/edit/<int:tour_id>/', views.edit_tour_view, name='edit_tour'),
    path('tour/delete/<int:tour_id>/', views.delete_tour_view, name='delete_tour'),
    path('tour/<int:tour_id>/', views.tour_detail_view, name='tour_detail'),

    # Payment
    path('subscription/payment/', views.agency_payment_view, name='agency_payment'),
]
