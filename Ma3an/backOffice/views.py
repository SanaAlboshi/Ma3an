from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Agency, Traveler, Notification
from backOffice.decorators import admin_only
from agency.models import Subscription

from backOffice.decorators import admin_only


@login_required
@admin_only
def dashboard(request):
    pending_agencies = Agency.objects.filter(approval_status=Agency.ApprovalStatus.PENDING).count()
    approved_agencies = Agency.objects.filter(approval_status=Agency.ApprovalStatus.APPROVED).count()

    context = {
        "pending_agencies": pending_agencies,
        "active_agencies": approved_agencies,
        "total_users": User.objects.count(),
        "subscriptions_count": Subscription.objects.count(),
        "recent_notifications": Notification.objects.filter(user=request.user).order_by("-created_at")[:5],
    }
    return render(request, "backOffice/dashboard.html", context)


@login_required
@admin_only
def manage_agencies(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "all").strip()

    agencies_qs = Agency.objects.select_related("user").all()

    if status == "pending":
        agencies_qs = agencies_qs.filter(approval_status=Agency.ApprovalStatus.PENDING)
    elif status == "approved":
        agencies_qs = agencies_qs.filter(approval_status=Agency.ApprovalStatus.APPROVED)
    elif status == "rejected":
        agencies_qs = agencies_qs.filter(approval_status=Agency.ApprovalStatus.REJECTED)

    if q:
        agencies_qs = agencies_qs.filter(
            Q(agency_name__icontains=q)
            | Q(commercial_license__icontains=q)
            | Q(city__icontains=q)
            | Q(phone_number__icontains=q)
            | Q(user__username__icontains=q)
            | Q(user__email__icontains=q)
        )

    agencies_qs = agencies_qs.order_by("-id")

    paginator = Paginator(agencies_qs, 8)
    agencies_page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "backOffice/agencies.html",
        {
            "agencies": agencies_page,
            "q": q,
            "status": status,
        },
    )


@login_required
@admin_only
def agency_detail(request, agency_id):
    agency = get_object_or_404(Agency.objects.select_related("user"), id=agency_id)
    return render(request, "backOffice/agency_detail.html", {"agency": agency})


@login_required
@admin_only
def approve_agency(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    if agency.approval_status != Agency.ApprovalStatus.APPROVED:
        agency.approval_status = Agency.ApprovalStatus.APPROVED
        agency.rejection_reason = ""
        agency.save()

        Notification.objects.create(
            user=agency.user,
            message=f"Your agency '{agency.agency_name}' has been approved.",
        )

    return redirect("backOffice:manage_agencies")


@login_required
@admin_only
@require_POST
def reject_agency(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    if agency.approval_status != Agency.ApprovalStatus.APPROVED:
        reason = request.POST.get("rejection_reason", "").strip()

        agency.approval_status = Agency.ApprovalStatus.REJECTED
        agency.rejection_reason = reason
        agency.save()

        Notification.objects.create(
            user=agency.user,
            message=f"Your agency '{agency.agency_name}' was rejected. Reason: {reason or 'No reason provided.'}",
        )

    return redirect("backOffice:manage_agencies")


@login_required
@admin_only
def manage_subscriptions(request):
    subscriptions = Subscription.objects.all().order_by("subscriptionType")
    return render(request, "backOffice/subscriptions.html", {"subscriptions": subscriptions})


@login_required
@admin_only
def users_list(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "backOffice/users.html", {"users": users})


@login_required
@admin_only
def system_security(request):
    return render(request, "backOffice/security.html")
