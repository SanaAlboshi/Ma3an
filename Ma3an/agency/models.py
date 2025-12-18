from django.db import models
# agency/models.py
from django.contrib.auth.models import User

class Agency(models.Model):
    name = models.CharField(max_length=200)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TourGuide(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Tour(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    travelers = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    tour_guide = models.ForeignKey(
        TourGuide,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    supervisor = models.ForeignKey(
        Supervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    image = models.ImageField(upload_to='tour_images/', null=True, blank=True)

    def __str__(self):
        return self.name

