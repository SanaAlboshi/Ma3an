from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm, AgencyForm, TourGuideCreateForm
from .models import Traveler, Agency, TourGuide, Language, Notification
from django.contrib import messages
import pycountry
from django.contrib.auth.decorators import login_required
# from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

def signup_role_view(request):
    return render(request, "accounts/signup_role.html")

def traveler_signup_view(request):
    
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

def agency_signup_view(request):
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
    
#agency creating tour guide
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
            return redirect("tourGuide:all_tourguides")
    else:
        form = TourGuideCreateForm()

    return render(request, "accounts/create_tourguide.html", {"form": form})


 #profile view for all 3 types of users   
@login_required
def profile_view(request):
    user = request.user
    edit_mode = request.GET.get('edit') == '1'

    profile = None

    if request.method == 'POST':
        #user base info
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

    #role-specific =====
    if user.role == 'traveler':
        profile, _ = Traveler.objects.get_or_create(user=user)

        if request.method == 'POST':
            profile.date_of_birth = request.POST.get('date_of_birth')
            profile.phone_number = request.POST.get('phone_number')
            profile.gender = request.POST.get('gender')
            profile.nationality = request.POST.get('nationality')
            profile.passport_number = request.POST.get('passport_number')
            profile.passport_expiry_date = request.POST.get('passport_expiry_date')
            profile.save()

    elif user.role == 'agency':
        profile, _ = Agency.objects.get_or_create(user=user)

        if request.method == 'POST':
            profile.agency_name = request.POST.get('agency_name')
            profile.phone_number = request.POST.get('phone_number')
            profile.city = request.POST.get('city')
            profile.commercial_license = request.POST.get('commercial_license')
            profile.save()

    elif user.role == 'tourGuide':
        profile, _ = TourGuide.objects.get_or_create(user=user)

        if request.method == 'POST':
            profile.phone = request.POST.get('phone')
            profile.gender = request.POST.get('gender')
            profile.nationality = request.POST.get('nationality')
            profile.passport_number = request.POST.get('passport_number')
            profile.passport_expiry_date = request.POST.get('passport_expiry_date')
            profile.is_active = bool(request.POST.get('is_active'))
            profile.save()

    countries = list(pycountry.countries)
    if request.method == 'POST':
        return redirect('accounts:profile_view')

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'edit_mode': edit_mode,
        'countries': countries,
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

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()

    next_url = request.GET.get("next")
    return redirect(next_url)
