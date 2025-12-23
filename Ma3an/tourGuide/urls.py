from django.urls import path
from . import views

app_name = "tourGuide"

urlpatterns = [
    path('all/guides/', views.all_tourguides_view, name='all_tourguides'),
    path('delete/<int:guide_id>/', views.delete_tourguide, name='delete_guide'),
    path('my/tours/', views.my_tours_view, name='my_tours'),


]