from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Tour, TourGuide
from .forms import TourForm

# agency/views.py
from django.contrib.auth.models import User
from .models import TourGuide, Agency
from django.contrib.auth.decorators import login_required

def add_tour_guide_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('add_tour_guide')

        # إنشاء المستخدم
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # إنشاء TourGuide بدون ربطه بوكالة
        TourGuide.objects.create(user=user)

        messages.success(request, 'TourGuide account created successfully ✅')
        return redirect('dashboard')

    return render(request, 'agency/add_tour_guide.html')


def all_tour_guides_view(request):
    tour_guides = TourGuide.objects.all()
    return render(request, 'agency/all_tour_guides.html', {'tour_guides': tour_guides})


# لوحة التحكم الخاصة بالوكالة
def dashboard_view(request):
    return render(request, 'agency/agency_dashboard.html')

# صفحة الاشتراك الخاصة بالوكالة
def subscription_view(request):
    return render(request, 'agency/agency_subscription.html')

# إضافة تور جديد
def add_tour_view(request):
    guides = TourGuide.objects.all()
    tour_guides = TourGuide.objects.all()  # عرض كل TourGuides بدون شرط

    if request.method == "POST":
        tour_guide_id = request.POST.get('tour_guide')
        tour_guide = TourGuide.objects.get(id=tour_guide_id) if tour_guide_id else None

        tour = Tour(
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            country=request.POST.get('country'),
            city=request.POST.get('city'),
            travelers=request.POST.get('travelers') or 0,
            price=request.POST.get('price') or 0,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            tour_guide=tour_guide
        )

        if 'image' in request.FILES:
            tour.image = request.FILES['image']

        tour.save()
        messages.success(request, '✅ Tour saved successfully!')
        return redirect('all_tours')

    return render(request, 'agency/add_tour.html', {
        'guides': guides,
        'tour_guides': tour_guides
    })

# عرض كل التورز
def all_tours_view(request):
    tours = Tour.objects.all()
    return render(request, 'agency/all_tours.html', {'tours': tours})

# حفظ التور باستخدام الفورم
def save_tour_view(request):
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Tour saved successfully!')
            return redirect('add_tour')  # إعادة التوجيه بعد الحفظ
    else:
        form = TourForm()

    tours = Tour.objects.all()
    return render(request, 'agency/add_tour.html', {'form': form, 'tours': tours})


def edit_tour_view(request, tour_id):
    try:
        tour = Tour.objects.get(id=tour_id)
    except Tour.DoesNotExist:
        messages.error(request, "Tour not found")
        return redirect('all_tours')

    guides = TourGuide.objects.all()

    if request.method == "POST":
        tour.name = request.POST.get('tourName')
        tour.description = request.POST.get('description')
        tour.country = request.POST.get('country')
        tour.city = request.POST.get('city')
        tour.travelers = request.POST.get('travelers') or 0
        tour.price = request.POST.get('price') or 0
        tour.start_date = request.POST.get('startDate')
        tour.end_date = request.POST.get('endDate')

        tour_guide_id = request.POST.get('tourGuide')
        if tour_guide_id:
            try:
                tour.tour_guide = TourGuide.objects.get(id=tour_guide_id)
            except TourGuide.DoesNotExist:
                tour.tour_guide = None

        if 'tourImage' in request.FILES:
            tour.image = request.FILES['tourImage']

        tour.save()
        messages.success(request, "✅ Tour updated successfully!")
        return redirect('all_tours')

    return render(request, 'agency/edit_tour.html', {'tour': tour, 'guides': guides})


def delete_tour_view(request, tour_id):
    try:
        tour = Tour.objects.get(id=tour_id)
        tour.delete()
        messages.success(request, "✅ Tour deleted successfully!")
    except Tour.DoesNotExist:
        messages.error(request, "Tour not found")
    return redirect('all_tours')


def tour_detail_view(request, tour_id):
    try:
        tour = Tour.objects.get(id=tour_id)
    except Tour.DoesNotExist:
        messages.error(request, "Tour not found")
        return redirect('all_tours')
    
    return render(request, 'agency/tour_detail.html', {'tour': tour})

def agency_payment_view(request):
    return render(request, 'agency/agency_payment.html')
