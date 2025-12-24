from django import forms
from .models import User, Traveler, Agency
import pycountry


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "password"]


GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
]

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
