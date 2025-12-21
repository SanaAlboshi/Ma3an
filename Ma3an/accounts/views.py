from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth import authenticate, login, logout
from .models import Traveler, Agency, TourGuide, Language, Notification
from django.contrib import messages
import pycountry

from django.conf import settings
User = settings.AUTH_USER_MODEL

# from django_countries import countries


# Create your views here.

def signup_view(request : HttpRequest):
    
    countries = [(c.alpha_2, c.name) for c in pycountry.countries]
    
    if request.method == "POST":
        role = request.POST.get("role")

        user = User.objects.create_user(
            role = request.POST["role"],
            email=request.POST["email"],
            username=request.POST["username"],
            password=request.POST["password"],
            first_name=request.POST.get("first_name", ""),
            last_name=request.POST.get("last_name", ""),
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
                phone_number=request.POST.get("phone_number"),
                license_number=request.POST.get("license_number"),
                city=request.POST.get("city"),
                address=request.POST.get("address"),
                commercial_license=request.POST.get("commercial_license"),
                approval_status="pending"
            )

        messages.success(request, "Account created successfully")
        return redirect("accounts:signin_view")
    return render(request, "accounts/signup.html",
                  {"countries": countries} 
                  #{"countries": list(countries)}
                  )



def signup_tourguide_view(request):
    # if not request.user.is_authenticated or request.user.role != "agency":
    #     messages.error(request, "Only registered agencies can add tour guides.")
    #     return redirect("accounts:signin_view")

    countries = [(c.alpha_2, c.name) for c in pycountry.countries]
    languages_list = Language.objects.all()
    
    # languages_list = [
    #     (lang.alpha_2, lang.name) 
    #     for lang in pycountry.languages 
    #     if hasattr(lang, "alpha_2")
    # ]

    if request.method == "POST":
        user = User.objects.create_user(
            email=request.POST["email"],
            username=request.POST.get("username", ""),
            first_name=request.POST.get("first_name", ""),
            last_name=request.POST.get("last_name", ""),
            password=request.POST["password"],
            role="tourGuide"
        )

        tour_guide = TourGuide.objects.create(
            user=user,
            agency=request.user.agency_profile,
            gender=request.POST["gender"],
            phone_number=request.POST.get("phone_number", ""),
            # languages=languages_str,
            nationality=request.POST.get("nationality"),
            passport_number=request.POST.get("passport_number"),
            passport_expiry_date=request.POST.get("passport_expiry_date"),
            is_active=True
        )
        
        # selected_languages = request.POST.getlist("languages")
        # languages_str = ",".join(selected_languages)

        selected_languages_ids = request.POST.getlist("languages")
        if selected_languages_ids:
            tour_guide.languages.set(selected_languages_ids)

        messages.success(request, "Tour Guide account created successfully")
        return redirect("agency_dashboard")

    return render(request, "accounts/tour_guide_signup.html", {
        "countries": countries,
        "languages": languages_list,
    })


        
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