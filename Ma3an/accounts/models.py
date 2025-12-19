from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)

    USERNAME_FIELD = 'email' 

    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='user',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )
    
    ROLE_CHOICES = (
        ("traveler", "Traveler"),
        ("agency", "Agency"),
        ("supervisor", "Supervisor"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        db_table = "CustomUser"


class Traveler(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = 'male'
        FEMALE = 'female'

    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'traveler_profile')
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(
        max_length=10,
        choices = GenderChoices.choices
    )
    nationality = CountryField()
    passport_number = models.CharField(max_length = 20, unique = True)
    passport_expiry_date = models.DateField()
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Agency(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    agency_name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    commercial_license = models.CharField(max_length=100)
    status = models.CharField(max_length=20, 
                              choices=(
                                  ("Pending","Pending"),
                                  ("Approved","Approved")), 
                                default="Pending")

    def __str__(self):
        return self.agency_name
    
    
class TourGuide(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name="tour_guides")
    phone_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"



class PrivacySettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="privacy_settings")
    show_email = models.BooleanField(default=True, help_text="Allow others to see your email")
    # show_bio = models.BooleanField(default=True, help_text="Allow others to see your bio")
    # show_portfolio = models.BooleanField(default=True, help_text="Allow others to see your portfolio")

    def str(self):
        return f"Privacy Settings for {self.user.username}"