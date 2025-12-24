from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts.models import Agency, TourGuide, Traveler
from django.contrib import messages
from agency.models import Tour
from datetime import date
from django.core.mail import send_mass_mail
from .forms import TourAnnouncementForm
# Create your views here.


@login_required
def all_tourguides_view(request):

    if request.user.role != 'agency':
        return redirect('accounts:profile')

    agency = request.user.agency_profile
    tour_guides = agency.tour_guides.select_related('user')

    return render(request, 'tourGuide/all_tourGuides.html', {
        'agency': agency,
        'tour_guides': tour_guides,
    })
    

@login_required
def delete_tourguide(request, guide_id):
    if request.user.role != 'agency':
        return redirect('accounts:profile')

    agency = request.user.agency_profile
    guide = get_object_or_404(TourGuide, id=guide_id, agency=agency)

    if request.method == 'POST':
        first_name = guide.user.first_name
        last_name = guide.user.last_name

        guide.user.delete()

        messages.success(
            request,
            f'Tour guide "{first_name} {last_name}" has been deleted successfully.'
        )

        return redirect('tourGuide:all_tourguides')

    return redirect('tourGuide:all_guides')


@login_required
def my_tours_view(request):
    tours = []

    if request.user.role == 'tourGuide':
        tours = Tour.objects.filter(tour_guide__user=request.user).order_by('-start_date')

    context = {
        'tours': tours
    }
    return render(request, 'tourguide/my_tours.html', context)


def tour_details_view(request, tour_id):
    if request.user.role != 'tourGuide':
        return redirect('accounts:profile')
    
    tour = get_object_or_404(Tour, id=tour_id, tour_guide__user=request.user)

    travelers = Traveler.objects.filter(tour__id=tour.id)

    context = {
        'tour': tour,
        'travelers': travelers,
        'today': date.today(),
    }

    return render(request, 'tourguide/tour_detail.html', context)


@login_required
def tourguide_dashboard_view(request):
    today = date.today()

    tours = Tour.objects.filter(tour_guide__user=request.user).order_by('-start_date')

    upcoming_tours_count = tours.filter(start_date__gt=today).count()
    active_tours_count = tours.filter(start_date__lte=today, end_date__gte=today).count()

    context = {
        'tours': tours,
        'upcoming_tours_count': upcoming_tours_count,
        'active_tours_count': active_tours_count,
        'today': today,
    }

    return render(request, 'tourguide/tourGuide_dashboard.html', context)




@login_required
def send_announcement_view(request, tour_id):
    from main.models import Tour

    try:
        tour = Tour.objects.get(id=tour_id, tour_guide__user=request.user)
    except Tour.DoesNotExist:
        messages.error(request, "Tour not found or you are not authorized.")
        return redirect('tourGuide:dashboard')

    if request.method == "POST":
        form = TourAnnouncementForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']

            # جلب الإيميلات لكل المسجلين في الرحلة
            recipients = tour.travelers_set.all()  # استبدلها حسب العلاقة الصحيحة للمسجلين
            emails = [traveler.user.email for traveler in recipients if traveler.user.email]

            # إعداد الرسائل الجماعية
            subject = f"Announcement for Tour: {tour.name}"
            from_email = "no-reply@yourdomain.com"
            messages_to_send = [(subject, message, from_email, [email]) for email in emails]

            send_mass_mail(messages_to_send)

            messages.success(request, "✅ Announcement sent successfully.")
            return redirect('tourGuide:dashboard')
    else:
        form = TourAnnouncementForm()

    return render(request, 'tourGuide/send_announcement.html', {'form': form, 'tour': tour})
