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

    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    amount = models.IntegerField(help_text="Amount in halalas")
    currency = models.CharField(max_length=3, default="SAR")
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    moyasar_id = models.CharField(max_length=64, blank=True, null=True, unique=True)
    transaction_url = models.URLField(blank=True, null=True)
    raw = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, default="")

class Review(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE)
    tour = models.ForeignKey("agency.Tour", on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
