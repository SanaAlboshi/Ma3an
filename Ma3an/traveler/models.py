from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Traveler(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="traveler")
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class TourJoin(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE)
    tour = models.ForeignKey("tours.Tour", on_delete=models.CASCADE)

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
    tour = models.ForeignKey("tours.Tour", on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
