from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Tour, TourSchedule
from datetime import datetime



# -------------------------
# Agency Views
# -------------------------
def dashboard_view(request):
    return render(request, 'agency/agency_dashboard.html')


def subscription_view(request):
    return render(request, 'agency/agency_subscription.html')


def agency_payment_view(request):
    return render(request, 'agency/agency_payment.html')


# -------------------------
# Tour Views
# -------------------------
def add_tour_view(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = end_date = None

    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if start_date > end_date:
                messages.error(request, "❌ تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية")
                start_date = end_date = None
        except ValueError:
            messages.error(request, "❌ تنسيق التواريخ غير صحيح")
            start_date = end_date = None

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        country = request.POST.get('country')
        city = request.POST.get('city')
        travelers = int(request.POST.get('travelers') or 0)
        price = float(request.POST.get('price') or 0)

        try:
            start_date = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d").date()
            end_date = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "❌ تنسيق التواريخ غير صحيح")
            return render(request, 'agency/add_tour.html', {
                'name': name,
                'description': description,
                'country': country,
                'city': city,
                'travelers': travelers,
                'price': price,
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
            })

        if start_date > end_date:
            messages.error(request, "❌ تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية")
            return render(request, 'agency/add_tour.html', {
                'name': name,
                'description': description,
                'country': country,
                'city': city,
                'travelers': travelers,
                'price': price,
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
            })

        # إنشاء الرحلة بدون TourGuide
        tour = Tour.objects.create(
            name=name,
            description=description,
            country=country,
            city=city,
            travelers=travelers,
            price=price,
            start_date=start_date,
            end_date=end_date,
        )

        messages.success(request, "✅ تم إنشاء الرحلة")
        return redirect('agency:add_schedule', tour_id=tour.id)


    return render(request, 'agency/add_tour.html', {
        'start_date': start_date_str,
        'end_date': end_date_str,
    })

def all_tours_view(request):
    tours = Tour.objects.all()
    tours_with_duration = []
    for tour in tours:
        duration_days = (tour.end_date - tour.start_date).days + 1
        tours_with_duration.append({
            'tour': tour,
            'duration': duration_days
        })
    return render(request, 'agency/all_tours.html', {'tours': tours_with_duration})


def edit_tour_view(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
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
        tour.tour_guide = TourGuide.objects.filter(id=tour_guide_id).first() if tour_guide_id else None

        if 'tourImage' in request.FILES:
            tour.image = request.FILES['tourImage']

        tour.save()
        messages.success(request, "✅ Tour updated successfully!")
        return redirect('all_tours')

    return render(request, 'agency/edit_tour.html', {'tour': tour, 'guides': guides})


def delete_tour_view(request, tour_id):
    tour = Tour.objects.filter(id=tour_id).first()
    if tour:
        tour.delete()
        messages.success(request, "✅ Tour deleted successfully!")
    else:
        messages.error(request, "Tour not found")
    return redirect('all_tours')


def tour_detail_view(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    schedules = tour.schedules.all()
    return render(request, 'agency/tour_detail.html', {
        'tour': tour,
        'schedules': schedules
    })

# -------------------------
# Tour Schedule Views
# -------------------------
def add_schedule_view(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    current_step = 1  # الخطوة الحالية افتراضياً

    if request.method == "POST":
        number_of_days = int(request.POST.get("number_of_days", 0))

        # إذا المستخدم اختار عدد الأيام فقط (الخطوة الثانية)
        if "set_days" in request.POST:
            current_step = 2
            days = range(1, number_of_days + 1)
            return render(request, "agency/add_schedule.html", {
                "tour": tour,
                "days": days,
                "number_of_days": number_of_days,
                "current_step": current_step
            })

        # إذا المستخدم أرسل الأنشطة (الخطوة الثالثة)
        else:
            current_step = 3
            days = range(1, number_of_days + 1)
            for day in days:
                start_times = request.POST.getlist(f"day_{day}_start_time[]")
                end_times = request.POST.getlist(f"day_{day}_end_time[]")
                titles = request.POST.getlist(f"day_{day}_activity_title[]")
                locations = request.POST.getlist(f"day_{day}_location_name[]")
                urls = request.POST.getlist(f"day_{day}_location_url[]")
                descriptions = request.POST.getlist(f"day_{day}_description[]")

                for i in range(len(titles)):
                    TourSchedule.objects.create(
                        tour=tour,
                        day_number=day,
                        start_time=start_times[i],
                        end_time=end_times[i],
                        activity_title=titles[i],
                        location_name=locations[i],
                        location_url=urls[i],
                        description=descriptions[i],
                    )

            messages.success(request, "✅ Schedule saved successfully!")
            return redirect("agency:tour_detail", tour_id=tour.id)

    # الصفحة قبل اختيار الأيام (الخطوة الأولى)
    return render(request, "agency/add_schedule.html", {
        "tour": tour,
        "current_step": current_step
    })



def delete_schedule_view(request, schedule_id):
    schedule = get_object_or_404(TourSchedule, id=schedule_id)
    tour_id = schedule.tour.id
    schedule.delete()
    messages.success(request, "✅ Activity deleted successfully!")
    return redirect("tour_detail", tour_id=tour_id)
