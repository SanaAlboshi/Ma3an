from django.db import models
from django.contrib.auth.models import User
from accounts.models import TourGuide


# class Agency(models.Model):
#     name = models.CharField(max_length=200)
#     owner = models.OneToOneField(User, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name

# class TourGuide(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
#     phone = models.CharField(max_length=20, blank=True, null=True)

#     def __str__(self):
#         return self.user.username

class Tour(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    travelers = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.PositiveIntegerField(default=1)  # عدد الأيام

    tour_guide = models.ForeignKey(
        TourGuide,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='tour_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class TourSchedule(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='schedules')
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
