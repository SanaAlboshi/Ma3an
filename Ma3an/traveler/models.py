from django.db import models
from django.utils import timezone
from accounts.models import Traveler
from agency.models import Tour

class TravelerLocation(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name="locations")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="GPS accuracy in meters"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Is this the current location"
    )

    recorded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.traveler} @ ({self.latitude}, {self.longitude})"
    

class TravelerPayment(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE)
    tour = models.ForeignKey("agency.Tour", on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE)
    tour = models.ForeignKey("agency.Tour", on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
