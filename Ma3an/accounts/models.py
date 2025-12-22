from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username']
    
    groups = models.ManyToManyField( 
            'auth.Group', 
            related_name='accounts_user_set', 
            blank=True, 
            help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', 
            related_query_name='user', ) 
    
    user_permissions = models.ManyToManyField( 
                       'auth.Permission', 
                       related_name='accounts_user_permissions_set', 
                       blank=True, 
                       help_text='Specific permissions for this user.', 
                       related_query_name='user', )
    
    class RoleChoices(models.TextChoices):
        TRAVELER = 'traveler', 'Traveler'
        AGENCY = 'agency', 'Agency'
        TOURGUIDE = 'tourGuide', 'Tour Guide'

    role = models.CharField(max_length=20, choices=RoleChoices)
    
    class Meta:
        db_table = "CustomUser"

class GenderChoices(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'

        
class Traveler(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'traveler_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices = GenderChoices.choices,
        null=True,
        blank=True
    )
    nationality = models.CharField(max_length=3, null=True, blank=True)  
    passport_number = models.CharField(max_length = 20, unique = True, null=True, blank=True)
    passport_expiry_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Agency(models.Model):
    class ApprovalStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agency_profile")
    agency_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    commercial_license = models.CharField(max_length=100, null=True, blank=True)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING
    )
    # subscription = models.ForeignKey("agency.Subscription", on_delete=models.SET_NULL, null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.agency_name
    
    class Meta:
        ordering = ['agency_name']

    
class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    
class TourGuide(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name="tour_guides")
    gender = models.CharField(
        max_length=10,
        choices = GenderChoices.choices,
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=50, unique=True,blank=True, null=True)
    languages = models.ManyToManyField(Language, related_name="tour_guides", null=True, blank=True)
    # languages = models.CharField(max_length=255)
    nationality = models.CharField(max_length=3, null=True, blank=True)
    passport_number = models.CharField(max_length = 20, unique=True, null=True, blank=True)
    passport_expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")

    event = models.ForeignKey("agency.GeofenceEvent", on_delete=models.CASCADE, related_name="notifications")

    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
