from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'System Admin'),
        ('agency', 'Tour Agency'),
        ('guide', 'Tour Guide'),
        ('traveler', 'Traveler'),
    )

    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username


class Subscription(models.Model):
    subscriptionType = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20)

    def __str__(self):
        return self.subscriptionType
    

class TravelAgency(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    agencyName = models.CharField(max_length=255)
    licenseNumber = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    approved = models.BooleanField(default=False)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    rejected = models.BooleanField(default=False)
    rejectionReason = models.TextField(blank=True)

    def __str__(self):
        return self.agencyName
    

class Notification(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.profile.role != 'admin':
                return HttpResponseForbidden("You do not have access to this page.")
        except Profile.DoesNotExist:
            return HttpResponseForbidden("Profile missing for this user.")
        return view_func(request, *args, **kwargs)
    return wrapper


# @login_required
# @admin_only
def manage_agencies(request):
    q = request.GET.get('q', '').strip()

    agencies = TravelAgency.objects.select_related('profile', 'profile__user').all()

    if q:
        agencies = agencies.filter(
            agencyName__icontains=q
        ) | agencies.filter(
            licenseNumber__icontains=q
        ) | agencies.filter(
            city__icontains=q
        )

    agencies = agencies.order_by('-id')

    return render(request, 'agencies.html', {
        'agencies': agencies,
        'q': q
    })


# @login_required
# @admin_only
def approve_agency(request, agency_id):
    agency = get_object_or_404(TravelAgency, id=agency_id)

    if not agency.approved:
        agency.approved = True
        agency.save()

        Notification.objects.create(
            user=request.user,
            notification_type='agency',
            title=f"Agency approved - {agency.agencyName}",
            message=f"{agency.agencyName} has been approved by the system admin."
        )

    return redirect('manage_agencies')
