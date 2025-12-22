from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_role_view, name="signup_role"),
    # path("signup/", views.signup_view, name="signup_view"),
    path('signup/traveler/', views.signup_traveler_view, name='signup_traveler'),
    path('signup/agency/', views.signup_agency_view, name='signup_agency'),

    path("signin/", views.signin_view, name="signin_view"),
    path("logout/", views.log_out_view, name="log_out_view"),
    # path("guide/signup/", views.signup_tourguide_view, name="signup_tourguide_view"),
    path("profile/", views.profile_view, name="profile_view"),
    path("guide/profile/", views.tourguide_profile_view, name="tourguide_profile_view"),
    path("create/guide/", views.create_tourguide_view, name="create_tourguide_view"),
]