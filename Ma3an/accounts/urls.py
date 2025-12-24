from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("choose/role/", views.signup_role_view, name="signup_role"),
    path('signup/traveler/', views.traveler_signup_view, name='traveler_signup'),
    path('signup/agency/', views.agency_signup_view, name='agency_signup'),
    path("create/guide/", views.create_tourguide_view, name="create_tourguide_view"),
    path("profile/", views.profile_view, name="profile_view"),
    path("signin/", views.signin_view, name="signin_view"),
    path("logout/", views.log_out_view, name="log_out_view"),
]