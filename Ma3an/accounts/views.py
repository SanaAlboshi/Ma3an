from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Traveler, Agency, Notification
from django.contrib import messages
from django_countries import countries

# Create your views here.

def signup_view(request : HttpRequest):
    
    if request.method == "POST":
        role = request.POST.get("role")

        user = User.objects.create_user(
            username=request.POST["username"],
            email=request.POST["email"],
            password=request.POST["password"],
            first_name=request.POST.get("first_name", ""),
            last_name=request.POST.get("last_name", ""),
            role=role
        )

        if role == "traveler":
            Traveler.objects.create(
                user=user,
                date_of_birth=request.POST["date_of_birth"],
                phone_number=request.POST["phone_number"],
                gender=request.POST["gender"],
                nationality=request.POST["nationality"],
                passport_number=request.POST["passport_number"],
                passport_expiry_date=request.POST["passport_expiry_date"]
            )

        elif role == "agency":
            Agency.objects.create(
                user=user,
                agency_name=request.POST.get("agency_name"),
                license_number=request.POST.get("license_number"),
                phone_number=request.POST.get("phone_number"),
                address=request.POST.get("address"),
                city=request.POST.get("city"),
                country=request.POST.get("country"),
                commercial_license=request.POST.get("commercial_license"),
                status="Pending"
            )

        messages.success(request, "Account created successfully")
        return redirect("accounts:signin_view")
    return render(request, "accounts/signup.html", {"countries": list(countries)})


# def signup_traveler_view(request : HttpRequest):
    
#     if request.method == "POST":
#         try:
#             new_user = User.objects.create_user(
#                 username = request.POST["username"],
#                 password = request.POST["password"],
#                 email = request.POST["email"],
#                 first_name = request.POST["first_name"],
#                 last_name = request.POST["last_name"],
#             )

#             new_user.save()

#             messages.success(request, "registered successfully", "alert-success")
#             return redirect("accounts:signin_view")
#         except Exception as e: 
#             print(e)
    
#     return render(request, "accounts/signup.html")


# def signup_agency_view(request : HttpRequest):
#     pass

# def signup_guide_view(request : HttpRequest):
#     pass
        
def signin_view(request : HttpRequest):
    
    if request.method == "POST":
        user = authenticate(request, username = request.POST["username"],
                password = request.POST["password"])
        
        if user:
            login(request, user)
            messages.success(request, "logged in successfuly", "alert-success")
            return redirect(request.GET.get("next", "/"))
        else:
            messages.error(request, "Please try again, your info is wrong", "alert-danger")
     
    return render(request, "accounts/signin.html", {})


def log_out_view(request : HttpRequest):
    
    logout(request)
    messages.success(request, "logged out successfuly", "alert-success")
    return redirect("main:home_view")

# @login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()

    next_url = request.GET.get("next")
    return redirect(next_url)