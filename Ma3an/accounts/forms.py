from django import forms
from django_countries.fields import CountryField
from .models import User, Traveler

# -----------------------
# Form لإنشاء User
# -----------------------
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

# -----------------------
# Form لإنشاء Traveler
# -----------------------
class TravelerForm(forms.ModelForm):
    class Meta:
        model = Traveler
        fields = [
            'date_of_birth',
            'phone_number',
            'gender',
            'nationality',
            'passport_number',
            'passport_expiry_date'
        ]
        widgets = {
            'gender': forms.Select(choices=Traveler.GenderChoices.choices),
            'nationality': forms.Select(choices=list(CountryField().choices))
        }

