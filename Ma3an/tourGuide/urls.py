from django.urls import path
from . import views

app_name = "tourGuide"

urlpatterns = [
    path('all/guides/', views.all_tourguides_view, name='all_tourguides'),
    path('delete/<int:guide_id>/', views.delete_tourguide, name='delete_guide'),
    path('my/tours/', views.my_tours_view, name='my_tours'),
    path('tour/<int:tour_id>/', views.tour_details_view, name='tour_details'),
    path('dashboard/', views.tourguide_dashboard_view, name='tourguide_dashboard'),
    path('send/announcement/', views.send_announcement_view, name='send_announcement'),
    # path('tour/<int:tour_id>/detail/', views.tour_detail_view, name='tour_detail'),

]