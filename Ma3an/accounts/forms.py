from django import forms
from .models import User, Traveler, Agency
import pycountry
from django.contrib.auth.forms import UserCreationForm

# from django.contrib.auth import get_user_model

# User = get_user_model()

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "password"]


GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
]


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class TravelerForm(forms.ModelForm):
    nationality = forms.ChoiceField(choices=[], required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)

    class Meta:
        model = Traveler
        fields = ["date_of_birth", "phone_number", "gender", "nationality", "passport_number", "passport_expiry_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        countries = [(country.name, country.name) for country in pycountry.countries]
        self.fields['nationality'].choices = [("", "Select Nationality")] + countries
        
        
class AgencyForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ["agency_name", "phone_number", "city", "commercial_license"]

class TourGuideCreateForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Tour guide email"})
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Temporary password"})
    )


# from django import forms
# from django_countries.fields import CountryField
# from .models import User, Traveler

# # -----------------------
# # Form لإنشاء User
# # -----------------------
# class UserForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
#     confirm_password = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'role']

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")

#         if password != confirm_password:
#             raise forms.ValidationError("Passwords do not match")

#         return cleaned_data

# # -----------------------
# # Form لإنشاء Traveler
# # -----------------------
# class TravelerForm(forms.ModelForm):
#     class Meta:
#         model = Traveler
#         fields = [
#             'date_of_birth',
#             'phone_number',
#             'gender',
#             'nationality',
#             'passport_number',
#             'passport_expiry_date'
#         ]
#         widgets = {
#             'gender': forms.Select(choices=Traveler.GenderChoices.choices),
#             'nationality': forms.Select(choices=list(CountryField().choices))
#         }

