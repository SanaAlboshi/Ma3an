from django.db import models
from accounts.models import Agency


class Tour(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    # هذا هو الـ Capacity
    travelers = models.PositiveIntegerField(
        help_text="Max capacity (number of travelers)"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.PositiveIntegerField(default=1)

    tour_guide = models.ForeignKey(
        "accounts.TourGuide",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='tour_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class TourSchedule(models.Model):
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    day_number = models.PositiveIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    activity_title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location_name = models.CharField(max_length=255)
    location_url = models.URLField(blank=True, null=True)

    # REQUIRED for Geofence
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.tour.name} - Day {self.day_number} - {self.activity_title}"


class Geofence(models.Model):
    schedule = models.OneToOneField(TourSchedule, on_delete=models.CASCADE, related_name="geofence")

    radius_meters = models.PositiveIntegerField(
        help_text="Allowed distance from activity location in meters"
    )

    is_active = models.BooleanField(default=True)
    trigger_on_enter = models.BooleanField(default=False)
    trigger_on_exit = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class GeofenceEvent(models.Model):
    EVENT_CHOICES = [
        ("enter", "Enter"),
        ("exit", "Exit"),
    ]

    tour_guide = models.ForeignKey(
        "accounts.TourGuide",
        on_delete=models.CASCADE,
        related_name="geofence_events"
    )

    traveler = models.ForeignKey(
        "accounts.Traveler",
        on_delete=models.CASCADE,
        related_name="geofence_events"
    )

    geofence = models.ForeignKey(
        Geofence,
        on_delete=models.CASCADE,
        related_name="events"
    )

    event_type = models.CharField(max_length=10, choices=EVENT_CHOICES)

    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at"]
        unique_together = ("traveler", "geofence", "event_type")

    def __str__(self):
        return f"{self.traveler} {self.event_type} {self.geofence}"


#Subscription

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    subscriptionType = models.CharField(max_length=20, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    tours_limit = models.IntegerField(null=True, blank=True)
    supervisors_limit = models.IntegerField(null=True, blank=True)
    travelers_limit = models.IntegerField(null=True, blank=True)
  
    def __str__(self):
        return f"{self.subscriptionType.capitalize()} - ${self.price}"
    


class AgencyPayment(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name="payments")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agency} - {self.subscription} - {self.status}"
