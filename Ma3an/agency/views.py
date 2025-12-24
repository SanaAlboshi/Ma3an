from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Avg, Count, IntegerField
from django.db.models.functions import Cast, Round
from django.core.paginator import Paginator
from decimal import Decimal
from .models import Tour, TourSchedule
import requests
from django.conf import settings
from django.urls import reverse
from .models import Subscription, AgencyPayment
from accounts.models import Agency
from django.contrib.auth.decorators import login_required
from accounts.models import TourGuide
from django.db.models import Sum
from traveler.models import TravelerPayment # استيراد موديل الدفع من تطبيق ترافل
from datetime import date, datetime
# -------------------------
# Agency Views
# -------------------------
from django.utils import timezone

@login_required
def my_tours_view(request):
    agency = request.user.agency_profile
    status = request.GET.get('status', 'upcoming')
    today = timezone.now().date()

    tours = Tour.objects.filter(agency=agency)

    if status == 'upcoming':
        tours = tours.filter(start_date__gt=today)
    elif status == 'active':
        tours = tours.filter(start_date__lte=today, end_date__gte=today)
    elif status == 'past':
        tours = tours.filter(end_date__lt=today)

    cities = tours.values_list('city', flat=True).distinct()

    return render(request, 'agency/my_tours.html', {
        'tours': tours,   # 👈 Tour objects مباشرة
        'cities': cities,
        'status': status,
    })







def confirm_tour_view(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    if request.method == 'POST':
        tour.confirmed = True  # لو عندك حقل confirmed في المودل
        tour.save()
        messages.success(request, 'Tour confirmed successfully!')
        return redirect('agency:all_tours')
    return redirect('agency:dashboard')




@login_required
def dashboard_view(request):
    # 1. جلب بروفايل الوكالة وتاريخ اليوم
    agency = getattr(request.user, 'agency_profile', None)
    today = date.today()

    # 2. جلب كافة رحلات هذه الوكالة
    all_tours = Tour.objects.filter(agency=agency)
    
    # جلب كائنات المرشدين الفعليين التابعين لهذه الوكالة
    tour_guides = TourGuide.objects.filter(agency=agency) 
    tour_guides_count = tour_guides.count()

    # 3. تقسيم الرحلات حسب التاريخ
    # الرحلات القادمة: التي لم تبدأ بعد
    upcoming_tours_count = all_tours.filter(start_date__gt=today).count()
    
    # الرحلات النشطة: التي بدأت ولم تنتهِ بعد
    active_tours_count = all_tours.filter(start_date__lte=today, end_date__gte=today).count()
    
    # الرحلات المنتهية: التي انتهى تاريخ نهايتها
    past_tours_count = all_tours.filter(end_date__lt=today).count()

    # 4. إحصائيات إضافية (المرشدين والمسافرين)
    tour_guides_count = TourGuide.objects.filter(agency=agency).count()
    travelers_count = TravelerPayment.objects.filter(
        tour__agency=agency, 
        status=TravelerPayment.Status.PAID
    ).count()

    # 5. تجهيز البيانات للإرسال
    context = {
        'agency': agency,
        'tour_guides': tour_guides,
        'upcoming_tours_count': upcoming_tours_count,
        'active_tours_count': active_tours_count,
        'past_tours_count': past_tours_count,
        'tour_guides_count': tour_guides_count,
        'travelers_count': travelers_count,
        'tours': all_tours.order_by('-id')[:4], # عرض أحدث 4 رحلات في الجدول
        'today': today,
    }
    return render(request, 'agency/agency_dashboard.html', context)


@login_required
def subscription_view(request):
    agency = getattr(request.user, 'agency_profile', None)
    current_subscription = None
    amount_paid = None

    if agency and agency.current_subscription:
            # إذا عنده اشتراك، نجيب بيانات الدفع الأخير
        current_subscription = agency.current_subscription
        last_payment = AgencyPayment.objects.filter(
            agency=agency,
            subscription=current_subscription,
            status=AgencyPayment.Status.PAID
        ).order_by('-id').first()  # آخر دفعة ناجحة
        if last_payment:
            amount_paid = last_payment.amount / 100  # تحويل هللات إلى ريال

        return render(request, 'agency/agency_subscription.html', {
            'current_subscription': current_subscription,
            'amount_paid': amount_paid,
        })
    else:
        # إذا ما عنده اشتراك، نعرض كل الباقات
        subscriptions = Subscription.objects.all().order_by('price')
        return render(request, 'agency/agency_subscription.html', {
            'subscriptions': subscriptions
        })


def agency_payment_view(request):
    return render(request, 'agency/agency_payment.html')





# -------------------------
# Tour Views
# -------------------------

# @login_required
# def add_tour_view(request):
#     agency = request.user.agency_profile
#     plan = agency.current_subscription

#     # 1. Check if agency has a subscription
#     if not plan:
#         messages.error(request, "❌ You must subscribe to a plan first to create tours.")
#         return redirect('agency:subscription_view')

#     # 2. Check total tours limit for the plan
#     current_tours_count = Tour.objects.filter(agency=agency).count()
#     if plan.tours_limit is not None and current_tours_count >= plan.tours_limit:
#         messages.error(request, "⚠️ Limit Reached: You have reached the maximum number of tours allowed by your plan.")
#         return redirect('agency:dashboard')

#     # Handle GET dates
#     start_date_str = request.GET.get('start_date')
#     end_date_str = request.GET.get('end_date')
    
#     if request.method == "POST":
#         name = request.POST.get('name')
#         description = request.POST.get('description')
#         country = request.POST.get('country')
#         city = request.POST.get('city')
#         travelers = int(request.POST.get('travelers') or 0)
#         price = float(request.POST.get('price') or 0)
        
#         # --- التحقق الصارم من عدد المسافرين المسموح به في الرحلة الواحدة ---
#         if plan.travelers_limit is not None and travelers > plan.travelers_limit:
#             messages.error(request, f"❌ Plan Error: Your plan allows a maximum of {plan.travelers_limit} travelers per tour.")
#             return render(request, 'agency/add_tour.html', {
#                 'name': name, 'description': description, 'country': country, 
#                 'city': city, 'travelers': travelers, 'price': price,
#                 'start_date': request.POST.get('start_date'), 'end_date': request.POST.get('end_date'),
#                 'current_step': 1
#             })

#         try:
#             start_date = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d").date()
#             end_date = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d").date()
#         except ValueError:
#             messages.error(request, "❌ تنسيق التواريخ غير صحيح")
#             return render(request, 'agency/add_tour.html', {
#                 'name': name,
#                 'description': description,
#                 'country': country,
#                 'city': city,
#                 'travelers': travelers,
#                 'price': price,
#                 'start_date': request.POST.get('start_date'),
#                 'end_date': request.POST.get('end_date'),
                
#             })
            
#     # adding tour guide        
#     tour_guides = TourGuide.objects.filter(agency=request.user.agency_profile)
#     # filtering tour guides according to start and end dates of their tours
#     if start_date_str and end_date_str:
#         try:
#             new_start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
#             new_end = datetime.strptime(end_date_str, "%Y-%m-%d").date()

#             tour_guides = tour_guides.exclude(
#                 tour__start_date__lte=new_end,
#                 tour__end_date__gte=new_start
#             ).distinct()
#         except ValueError:
#             pass

#         if start_date > end_date:
#             messages.error(request, "❌ تاريخ البداية لا يمكن أن يكون بعد تاريخ النهاية")
#             return render(request, 'agency/add_tour.html', {
#                 'name': name,
#                 'description': description,
#                 'country': country,
#                 'city': city,
#                 'travelers': travelers,
#                 'price': price,
#                 'start_date': request.POST.get('start_date'),
#                 'end_date': request.POST.get('end_date'),
#             })

#         # إنشاء الرحلة بدون TourGuide
#         tour = Tour.objects.create(
#             name=name,
#             description=description,
#             country=country,
#             city=city,
#             travelers=travelers,
#             price=price,
#             start_date=start_date,
#             end_date=end_date,
#             agency=agency,
#         )

#         messages.success(request, "✅ تم إنشاء الرحلة")
#         return redirect('agency:add_schedule', tour_id=tour.id)


#     return render(request, 'agency/add_tour.html', {
#         'start_date': start_date_str,
#         'end_date': end_date_str,
#         'current_step': 1,
#         'tour_guides': tour_guides,
#     })




@login_required
def add_tour_view(request):
    start_date = None
    end_date = None

    agency = request.user.agency_profile
    plan = agency.current_subscription

    # Handle GET dates
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # إضافة Tour Guides للعرض في الـ dropdown
    tour_guides = TourGuide.objects.filter(agency=agency)

    # فلترة Tour Guides حسب تواريخ الرحلات إن وجدت
    if start_date_str and end_date_str:
        try:
            new_start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            new_end = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            tour_guides = tour_guides.exclude(
                tour__start_date__lte=new_end,
                tour__end_date__gte=new_start
            ).distinct()
        except ValueError:
            pass

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        country = request.POST.get('country')
        city = request.POST.get('city')
        travelers = int(request.POST.get('travelers') or 0)
        price = float(request.POST.get('price') or 0)

        # اختيار الـ Tour Guide
        tour_guide_id = request.POST.get('tour_guide')
        tour_guide = TourGuide.objects.filter(id=tour_guide_id).first() if tour_guide_id else None

        # التحقق من التواريخ
        try:
            start_date = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d").date()
            end_date = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d").date()

            if start_date > end_date:
                messages.error(request, "❌ Error: Start date cannot be after end date.")
                return render(request, 'agency/add_tour.html', {
                    'name': name, 'description': description, 'country': country, 
                    'city': city, 'travelers': travelers, 'price': price,
                    'start_date': request.POST.get('start_date'), 'end_date': request.POST.get('end_date'),
                    'tour_guides': tour_guides, 'current_step': 1
                })

            # ⭐⭐ إنشاء الرحلة (داخل الـ POST) ⭐⭐
            tour = Tour.objects.create(
                name=name,
                description=description,
                country=country,
                city=city,
                travelers=travelers,
                price=price,
                start_date=start_date,
                end_date=end_date,
                agency=agency,
                image=request.FILES.get('image')  # ← هذا السطر الجديد

            )
            messages.success(request, "✅ Tour created successfully!")
            return redirect('agency:add_schedule', tour_id=tour.id)

        except (ValueError, TypeError):
            messages.error(request, "❌ Error: Invalid date format.")
            return render(request, 'agency/add_tour.html', {
                'name': name,
                'description': description,
                'country': country,
                'city': city,
                'travelers': travelers,
                'price': price,
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
                'current_step': 1,
                'tour_guides': tour_guides,
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
                'current_step': 1,
                'tour_guides': tour_guides,
            })

        # ✅ إنشاء الرحلة مع Tour Guide
        tour = Tour.objects.create(
            name=name,
            description=description,
            country=country,
            city=city,
            travelers=travelers,
            price=price,
            start_date=start_date,
            end_date=end_date,
            agency=agency,
            tour_guide=tour_guide
        )

        messages.success(request, "✅ تم إنشاء الرحلة")
        return redirect('agency:add_schedule', tour_id=tour.id)

    return render(request, 'agency/add_tour.html', {
        'start_date': start_date_str,
        'end_date': end_date_str,
        'current_step': 1,
        'tour_guides': tour_guides,
    })








def all_tours_view(request):
    tours = (
        Tour.objects
        .annotate(
            avg_rating_raw=Avg("reviews__rating"),
        )
        .annotate(
            avg_rating=Cast(Round("avg_rating_raw"), IntegerField()),
            reviews_count=Count("reviews")
        )
        .order_by("-avg_rating", "-reviews_count", "-id")
    )

    # ===== Search (by tour name + by agency name) =====
    query = request.GET.get("q", "").strip()
    if query:
        tours = tours.filter(
            Q(name__icontains=query) |
            Q(agency__agency_name__icontains=query)
        )

    from decimal import Decimal

    # ===== فلترة الوجهة =====
    destination = request.GET.get('destination')
    if destination and destination != "All":
        tours = tours.filter(city__iexact=destination)

    # ===== فلترة عدد الأيام (باستخدام days فقط) =====
    duration = request.GET.get('duration')
    if duration == '1-3':
        tours = tours.filter(days__gte=1, days__lte=3)
    elif duration == '4-7':
        tours = tours.filter(days__gte=4, days__lte=7)
    elif duration == '7+':
        tours = tours.filter(days__gte=8)

    # ===== فلترة السعر =====
    price_range = request.GET.get('price_range')
    if price_range == '0-1000':
        tours = tours.filter(price__lte=Decimal("1000"))
    elif price_range == '1000-5000':
        tours = tours.filter(price__gte=Decimal("1000"), price__lte=Decimal("5000"))
    elif price_range == '5000+':
        tours = tours.filter(price__gte=Decimal("5000"))

     # ===== Pagination =====
    paginator = Paginator(tours, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ===== إعداد قائمة المدن =====
    cities = (
        Tour.objects
        .order_by('city')
        .values_list('city', flat=True)
        .distinct()
    )

    # ===== تجهيز البيانات للعرض =====
    tours_with_duration = [
        {
            'tour': tour,
            'duration': tour.days
        }
        for tour in tours
    ]


    return render(request, 'agency/all_tours.html', {
        'page_obj': page_obj,
        'cities': cities,  # قائمة المدن للفلتر
        'selected_destination': destination,
        'selected_duration': duration,
        'selected_price_range': price_range,
        'search_query': query,
    })


def tour_detail_view(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    schedules = tour.schedules.all()
    return render(request, 'agency/tour_detail.html', {
        'tour': tour,
        'schedules': schedules,
        'current_step': 3
        
    })
@login_required
def edit_tour_view(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id, agency=request.user.agency_profile)
    schedules = TourSchedule.objects.filter(tour=tour).order_by('day_number', 'start_time')
    tour_guides = TourGuide.objects.filter(agency=request.user.agency_profile)

    if request.method == 'POST':
        # 1. تحديث بيانات الرحلة الأساسية
        tour.name = request.POST.get('name')
        tour.description = request.POST.get('description')
        tour.country = request.POST.get('country')
        tour.city = request.POST.get('city')
        tour.travelers = int(request.POST.get('travelers') or 0)
        tour.price = float(request.POST.get('price') or 0)

        if 'image' in request.FILES:
            tour.image = request.FILES['image']

        guide_id = request.POST.get('tour_guide')
        tour.tour_guide_id = guide_id if guide_id else None
        tour.save()

        # 2. تحديث الأنشطة الموجودة
        for schedule in schedules:
            # التحقق إذا كان المستخدم ضغط على زر الحذف
            if f"schedule_{schedule.id}_delete" in request.POST:
                schedule.delete()
                continue

            # جلب البيانات مع وضع قيم افتراضية للحقول الإجبارية لتجنب IntegrityError
            schedule.start_time = request.POST.get(f"schedule_{schedule.id}_start")
            schedule.end_time = request.POST.get(f"schedule_{schedule.id}_end")
            schedule.activity_title = request.POST.get(f"schedule_{schedule.id}_title")
            
            # حل مشكلة NOT NULL: إذا كان الحقل فارغاً نضع قيمة نصية
            location = request.POST.get(f"schedule_{schedule.id}_location")
            schedule.location_name = location if location else "TBA" # To Be Announced
            
            schedule.description = request.POST.get(f"schedule_{schedule.id}_desc")
            
            # حفظ التعديلات
            schedule.save()

        # 3. إضافة أنشطة جديدة (إن وجدت)
        new_titles = request.POST.getlist("new_title[]")
        new_days = request.POST.getlist("new_day[]")
        new_locations = request.POST.getlist("new_location[]") # تأكدي من وجودها في JS

        for i in range(len(new_titles)):
            if not new_titles[i].strip():
                continue
                
            TourSchedule.objects.create(
                tour=tour,
                day_number=new_days[i] if new_days[i] else 1,
                start_time=request.POST.getlist("new_start[]")[i],
                end_time=request.POST.getlist("new_end[]")[i],
                activity_title=new_titles[i],
                location_name=new_locations[i] if (len(new_locations) > i and new_locations[i]) else "TBA",
                description=request.POST.getlist("new_desc[]")[i],
            )

        messages.success(request, "✅ Tour updated successfully!")
        return redirect('agency:my_tours')

    return render(request, 'agency/edit_tour.html', {
        'tour': tour,
        'tour_guides': tour_guides,
        'schedules': schedules,
    })


@login_required
def delete_tour_view(request, tour_id):
    # جلب الرحلة والتأكد أنها تابعة لوكالة المستخدم الحالي فقط لزيادة الأمان
    tour = get_object_or_404(Tour, id=tour_id, agency=request.user.agency_profile)
    
    if request.method == 'POST':
        tour.delete()
        messages.success(request, "✅ تم حذف الرحلة بنجاح.")
        return redirect('agency:my_tours')
    
    # في حال محاولة الوصول للدالة عبر GET (رابط مباشر)
    return redirect('agency:my_tours')
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
                latitudes = request.POST.getlist(f"day_{day}_latitude[]")
                longitudes = request.POST.getlist(f"day_{day}_longitude[]")

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
                        latitude=latitudes[i],
                        longitude=longitudes[i],
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

@login_required
def select_subscription_view(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    agency = request.user.agency_profile

    if request.method == "POST":
        # 1. إنشاء سجل الدفع في قاعدة بياناتك أولاً
        payment = AgencyPayment.objects.create(
            agency=agency,
            subscription=subscription,
            amount=int(subscription.price * 100),  # تحويل من ريال إلى هللة
            currency="SAR",
            description=f"Subscription: {subscription.subscriptionType}",
        )

        # 2. تجهيز روابط العودة لموقعك
        # هذا الرابط ميسر يرسل عليه نتيجة الدفع (الخلفية)
        callback_url = request.build_absolute_uri(reverse('agency:subscription_callback'))
        
        # 3. تجهيز بيانات الطلب (Payload)
        payload = {
            "amount": payment.amount,
            "currency": payment.currency,
            "description": payment.description,
            "callback_url": callback_url,
            "back_url": callback_url,  # 👈 هذا السطر هو المسؤول عن "التحويل التلقائي" بعد الدفع
        }

        try:
            # 4. إرسال الطلب لميسر لإنشاء الفاتورة
            r = requests.post(
                f"{settings.MOYASAR_BASE_URL_AGENCY}/invoices",
                auth=(settings.MOYASAR_SECRET_KEY_AGENCY, ""),
                json=payload,
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()

            # 5. حفظ البيانات المستلمة من ميسر
            payment.moyasar_id = data.get("id")
            payment.transaction_url = data.get("url")
            payment.raw = data
            payment.save()

            # 6. تحويل المستخدم لصفحة الدفع الخاصة بميسر
            if payment.transaction_url:
                return redirect(payment.transaction_url)
            else:
                messages.error(request, "لم يتم استلام رابط الدفع من ميسر.")
                return redirect("agency:subscription_view")

        except Exception as e:
            messages.error(request, f"خطأ في الاتصال بميسر: {str(e)}")
            return redirect("agency:subscription_view")

    # في حال كان الطلب GET نعرض صفحة التأكيد
    return render(request, "agency/select_subscription.html", {
        "subscription": subscription,
        "agency": agency,
    })






@login_required
def subscription_callback_view(request):
    moyasar_id = request.GET.get("id")
    
    if not moyasar_id:
        return redirect("agency:dashboard")

    payment = get_object_or_404(AgencyPayment, moyasar_id=moyasar_id)

    try:
        r = requests.get(
            f"{settings.MOYASAR_BASE_URL_AGENCY}/payments/{moyasar_id}",
            auth=(settings.MOYASAR_SECRET_KEY_AGENCY, ""),
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        status = data.get("status")

        if status == 'paid':
            # تحديث قاعدة البيانات وتفعيل الاشتراك
            payment.status = AgencyPayment.Status.PAID
            payment.save()
            
            agency = payment.agency
            agency.current_subscription = payment.subscription
            agency.save()

            # 👈 بدلاً من الـ redirect، سنعرض صفحة نجاح
            return render(request, "agency/payment_success.html", {
                "payment": payment,
                "subscription": payment.subscription
            })
        else:
            messages.error(request, "عذراً، لم تكتمل عملية الدفع.")
            return redirect("agency:subscription_view")

    except Exception as e:
        messages.error(request, "حدث خطأ أثناء معالجة الطلب.")
        return redirect("agency:subscription_view")