from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Agency, Traveler, Notification
from backOffice.decorators import admin_only
from agency.models import Subscription

from backOffice.decorators import admin_only

from django.contrib.auth.decorators import login_required


User = get_user_model()



@login_required(login_url="/admin/login/")
@admin_only
def dashboard(request):
    pending_agencies = Agency.objects.filter(
        approval_status=Agency.ApprovalStatus.PENDING
    ).count()

    approved_agencies = Agency.objects.filter(
        approval_status=Agency.ApprovalStatus.APPROVED
    ).count()

    recent_notifications = Notification.objects.order_by("-created_at")[:5]

    context = {
        "pending_agencies": pending_agencies,
        "active_agencies": approved_agencies,
        "total_users": User.objects.count(),
        "subscriptions_count": Subscription.objects.count(),
        "recent_notifications": recent_notifications,
    }
    return render(request, "backOffice/dashboard.html", context)


@login_required(login_url="/admin/login/")
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


@login_required(login_url="/admin/login/")
@admin_only
def agency_detail(request, agency_id):
    agency = get_object_or_404(Agency.objects.select_related("user"), id=agency_id)
    return render(request, "backOffice/agency_detail.html", {"agency": agency})


@login_required(login_url="/admin/login/")
@admin_only
def approve_agency(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    if agency.approval_status != Agency.ApprovalStatus.APPROVED:
        agency.approval_status = Agency.ApprovalStatus.APPROVED
        agency.rejection_reason = ""
        agency.save()

        # Notify the agency owner
        Notification.objects.create(
            user=agency.user,
            message=f"Your agency '{agency.agency_name}' has been approved.",
        )

    return redirect("backOffice:manage_agencies")


@login_required(login_url="/admin/login/")
@admin_only
# @require_POST
def reject_agency(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    if agency.approval_status != Agency.ApprovalStatus.APPROVED:
        reason = request.POST.get("rejection_reason", "").strip()

        agency.approval_status = Agency.ApprovalStatus.REJECTED
        agency.rejection_reason = reason
        agency.save()

        # Notify the agency owner
        Notification.objects.create(
            user=agency.user,
            message=f"Your agency '{agency.agency_name}' was rejected. Reason: {reason or 'No reason provided.'}",
        )

    return redirect("backOffice:manage_agencies")


@login_required(login_url="/admin/login/")
@admin_only
def manage_subscriptions(request):
    q = request.GET.get("q", "").strip()

    subs = AgencySubscription.objects.select_related("agency", "agency__user", "plan").all()

    if q:
        subs = subs.filter(
            Q(agency__agency_name__icontains=q)
            | Q(agency__user__username__icontains=q)
            | Q(agency__user__email__icontains=q)
            | Q(plan__subscriptionType__icontains=q)
        )

    subs = subs.order_by("expiry_date")

    return render(request, "backOffice/manage_subscriptions.html", {"subs": subs, "q": q})


@login_required(login_url="/admin/login/")
@admin_only
def users_list(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "backOffice/users.html", {"users": users})



@login_required(login_url="/admin/login/")
@admin_only
def edit_subscription(request, sub_id):
    sub = get_object_or_404(AgencySubscription.objects.select_related("agency", "plan"), id=sub_id)
    plans = Subscription.objects.all().order_by("subscriptionType")

    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        status = request.POST.get("status")
        expiry_date = request.POST.get("expiry_date")

        if plan_id:
            sub.plan_id = int(plan_id)
        if status:
            sub.status = status
        if expiry_date:
            sub.expiry_date = expiry_date

        sub.save()
        return redirect("backOffice:manage_subscriptions")

    return render(
        request,
        "backOffice/edit_subscription.html",
        {
            "sub": sub,
            "plans": plans,
            "status_choices": AgencySubscription.Status.choices,
        },
    )

@login_required(login_url="/admin/login/")
@admin_only
@require_POST
def renew_subscription(request, sub_id):
    sub = get_object_or_404(AgencySubscription, id=sub_id)

    days = int(request.POST.get("days", "30"))
    today = timezone.localdate()

    if sub.expiry_date and sub.expiry_date >= today:
        sub.expiry_date = sub.expiry_date + timedelta(days=days)
    else:
        sub.expiry_date = today + timedelta(days=days)

    sub.status = AgencySubscription.Status.ACTIVE
    sub.save()

    return redirect("backOffice:manage_subscriptions")
