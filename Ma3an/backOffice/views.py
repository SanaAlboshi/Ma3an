from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q

from backOffice.decorators import admin_only
from backOffice.models import TravelAgency, Notification, Profile
from agency.models import Subscription


@login_required
@admin_only
def dashboard(request):
    context = {
        'pending_agencies': TravelAgency.objects.filter(approved=False, rejected=False).count(),
        'active_agencies': TravelAgency.objects.filter(approved=True).count(),
        'total_users': Profile.objects.count(),
        'active_subscriptions': Subscription.objects.filter(status='active').count(),
        'recent_notifications': Notification.objects.order_by('-created_at')[:5],
    }
    return render(request, 'backOffice/dashboard.html', context)


@login_required
# @admin_only
def manage_agencies(request):
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'all').strip()

    agencies_qs = TravelAgency.objects.select_related('profile', 'profile__user').all()

    if status == 'pending':
        agencies_qs = agencies_qs.filter(approved=False, rejected=False)
    elif status == 'approved':
        agencies_qs = agencies_qs.filter(approved=True)
    elif status == 'rejected':
        agencies_qs = agencies_qs.filter(rejected=True)

    if q:
        agencies_qs = agencies_qs.filter(
            Q(agencyName__icontains=q) |
            Q(licenseNumber__icontains=q) |
            Q(city__icontains=q) |
            Q(country__icontains=q)
        )

    agencies_qs = agencies_qs.order_by('-id')

    paginator = Paginator(agencies_qs, 8)
    page_number = request.GET.get('page')
    agencies_page = paginator.get_page(page_number)

    return render(request, 'backOffice/agencies.html', {
        'agencies': agencies_page,
        'q': q,
        'status': status,
    })


@login_required
# @admin_only
def approve_agency(request, agency_id):
    agency = get_object_or_404(TravelAgency, id=agency_id)

    if not agency.approved:
        agency.approved = True
        agency.rejected = False
        agency.rejectionReason = ''
        agency.save()

        Notification.objects.create(
            user=request.user,
            notification_type='agency',
            title=f"Agency approved: {agency.agencyName}",
            message=f"{agency.agencyName} has been approved by the system admin."
        )

    return redirect('manage_agencies')



@login_required
def manage_subscriptions(request):
    subscriptions = Subscription.objects.all()
    return render(request, 'backOffice/subscriptions.html', {'subscriptions': subscriptions})


@login_required
def users_list(request):
    users = User.objects.all()
    return render(request, 'backOffice/users.html', {'users': users})


@login_required
def system_security(request):
    return render(request, 'backOffice/security.html')




@login_required
# @admin_only
def agency_detail(request, agency_id):
    agency = get_object_or_404(TravelAgency.objects.select_related('profile', 'profile__user'), id=agency_id)
    return render(request, 'backOffice/agency_detail.html', {'agency': agency})


@login_required
# @admin_only
@require_POST
def reject_agency(request, agency_id):
    agency = get_object_or_404(TravelAgency, id=agency_id)

    if not agency.approved:
        agency.rejected = True
        agency.rejectionReason = request.POST.get('rejectionReason', '').strip()
        agency.save()

        Notification.objects.create(
            user=request.user,
            notification_type='agency',
            title=f"Agency rejected: {agency.agencyName}",
            message=agency.rejectionReason or "No reason provided."
        )

    return redirect('manage_agencies')


@login_required
@admin_only
def agency_detail(request, agency_id):
    agency = get_object_or_404(
        TravelAgency.objects.select_related('profile', 'profile__user'),
        id=agency_id
    )
    return render(request, 'backOffice/agency_detail.html', {'agency': agency})


@login_required
@admin_only
def manage_subscriptions(request):
    subscriptions = Subscription.objects.all()
    return render(request, 'backOffice/subscriptions.html', {'subscriptions': subscriptions})


@login_required
@admin_only
def users_list(request):
    users = User.objects.all()
    return render(request, 'backOffice/users.html', {'users': users})


@login_required
@admin_only
def system_security(request):
    return render(request, 'backOffice/security.html')
