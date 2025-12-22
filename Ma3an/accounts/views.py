from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm, TravelerForm, AgencyForm, TourGuideCreateForm, UserRegisterForm
from .models import Traveler, Agency, TourGuide, Language, Notification
from django.contrib import messages
import pycountry

# import random
# import string
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string

# from django.conf import settings
# User = settings.AUTH_USER_MODEL

from django.contrib.auth import get_user_model


User = get_user_model()

# Create your views here.

# views.py
def signup_role_view(request):
    return render(request, "accounts/signup_role.html")






def register_register_view(request):
    
    if request.method == "POST":
        try:
            new_user = User.objects.create_user(
                username = request.POST["username"],
                password = request.POST["password"],
                email = request.POST["email"],
                first_name = request.POST["first_name"],
                last_name = request.POST["last_name"],
            )

            new_user.save()

            messages.success(request, "registered successfully", "alert-success")
            return redirect("accounts:signin_view")
        except Exception as e: 
            print(e)
    
    return render(request, "accounts/traveler_signup.html")


    # if request.method == 'POST':
    #     form = UserRegisterForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('login')  # أو أي صفحة تريد إعادة التوجيه لها
    # else:
    #     form = UserRegisterForm()
    # return render(request, 'accounts/register.html', {'form': form})







def signup_traveler_view(request):
    # countries = [(country.name, country.name) for country in pycountry.countries]

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        traveler_form = TravelerForm(request.POST)

        if user_form.is_valid() and traveler_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.role = "traveler"
            user.save()

            traveler = traveler_form.save(commit=False)
            traveler.user = user
            traveler.save()

            messages.success(request, "Account created successfully.")
            return redirect('accounts:signin_view')
        else:
            print(user_form.errors)
            print(traveler_form.errors)
    else:
        user_form = UserForm()
        traveler_form = TravelerForm()

    context = {
        'user_form': user_form,
        'traveler_form': traveler_form,
        # 'countries': countries
    }
    return render(request, 'accounts/traveler_signup.html', context)



    # if not request.user.is_authenticated or request.user.role != "agency":
    #     messages.error(request, "Only agencies can create tour guides.")
    #     return redirect("accounts:signin_view")

    # if request.method == "POST":
    #     email = request.POST["email"]
    #     password = request.POST["password"]

    #     user = User.objects.create_user(
    #         email=email,
    #         username=email,
    #         password=password,
    #         role="tourGuide"
    #     )

    #     TourGuide.objects.create(
    #         user=user,
    #         agency=request.user.agency_profile,
    #         is_active=True
    #     )

    #     messages.success(request, "Tour guide created successfully.")
    #     return redirect("agency:dashboard")

    # return render(request, "accounts/create_tourguide.html")



def signup_agency_view(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        agency_form = AgencyForm(request.POST)

        if user_form.is_valid() and agency_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.role = "agency"
            user.save()

            agency = agency_form.save(commit=False)
            agency.user = user
            agency.approval_status = "pending"
            agency.save()

            messages.success(request, "Agency account created successfully.")
            return redirect("accounts:signin_view")
    else:
        user_form = UserForm()
        agency_form = AgencyForm()

    return render(request, "accounts/agency_signup.html", {
        "user_form": user_form,
        "agency_form": agency_form,
    })


# def tourguide_profile_view(request):
#     # if not request.user.is_authenticated or request.user.role != "agency":
#     #     messages.error(request, "Only registered agencies can add tour guides.")
#     #     return redirect("accounts:signin_view")

#     countries = [(c.alpha_2, c.name) for c in pycountry.countries]
#     languages_list = Language.objects.all()
    
#     # languages_list = [
#     #     (lang.alpha_2, lang.name) 
#     #     for lang in pycountry.languages 
#     #     if hasattr(lang, "alpha_2")
#     # ]

#     if request.method == "POST":
#         user = User.objects.create_user(
#             email=request.POST["email"],
#             username=request.POST.get("username", ""),
#             first_name=request.POST.get("first_name", ""),
#             last_name=request.POST.get("last_name", ""),
#             password=request.POST["password"],
#             role="tourGuide"
#         )

#         tour_guide = TourGuide.objects.create(
#             user=user,
#             agency=request.user.agency_profile,
#             gender=request.POST["gender"],
#             phone_number=request.POST.get("phone_number", ""),
#             # languages=languages_str,
#             nationality=request.POST.get("nationality"),
#             passport_number=request.POST.get("passport_number"),
#             passport_expiry_date=request.POST.get("passport_expiry_date"),
#             is_active=True
#         )
        
#         # selected_languages = request.POST.getlist("languages")
#         # languages_str = ",".join(selected_languages)

#         selected_languages_ids = request.POST.getlist("languages")
#         if selected_languages_ids:
#             tour_guide.languages.set(selected_languages_ids)

#         messages.success(request, "Tour Guide account created successfully")
#         return redirect("agency_dashboard")

#     return render(request, "accounts/tour_guide_signup.html", {
#         "countries": countries,
#         "languages": languages_list,
#     })



# @login_required
def tourguide_profile_view(request):
    if request.user.role != "tourGuide":
        messages.error(request, "Access denied.")
        return redirect("accounts:signin_view")

    tour_guide = request.user.tourguide
    languages = Language.objects.all()
    countries = [(c.alpha_2, c.name) for c in pycountry.countries]

    if request.method == "POST":
        # بيانات User
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.save()

        # بيانات TourGuide
        tour_guide.gender = request.POST.get("gender")
        tour_guide.phone = request.POST.get("phone")
        tour_guide.nationality = request.POST.get("nationality")
        tour_guide.passport_number = request.POST.get("passport_number")
        tour_guide.passport_expiry_date = request.POST.get("passport_expiry_date")

        selected_languages = request.POST.getlist("languages")
        tour_guide.languages.set(selected_languages)

        tour_guide.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("tourguide_profile")

    return render(request, "accounts/tourguide_profile.html", {
        "tour_guide": tour_guide,
        "languages": languages,
        "countries": countries
    })






# def generate_temp_password(length=8):
#     letters = string.ascii_letters + string.digits
#     return ''.join(random.choice(letters) for i in range(length))


def create_tourguide_view(request: HttpRequest):

    if not request.user.is_authenticated or request.user.role != "agency":
        messages.error(request, "Only agencies can create tour guides.")
        return redirect("accounts:signin_view")

    if request.method == "POST":
        form = TourGuideCreateForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.create_user(
                email=email,
                username=email,
                password=password,
                role="tourGuide"
            )

            TourGuide.objects.create(
                user=user,
                agency=request.user.agency_profile,
                is_active=True
            )

            messages.success(request, "Tour guide created successfully.")
            return redirect("main:home_view")
    else:
        form = TourGuideCreateForm()

    return render(request, "accounts/create_tourguide.html", {"form": form})
        
        
        
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


def profile_view(request):
    user = request.user

    if user.role == "traveler":
        template = "accounts/traveler_profile.html"
    elif user.role == "agency":
        template = "accounts/agency_profile.html"
    else:
        return redirect("home")

    return render(request, template, {"user": user})
