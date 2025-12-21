from django import forms
from .models import Tour, TourSchedule

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ['name', 'description', 'country', 'city', 'travelers', 'price', 'start_date', 'end_date']

class TourScheduleForm(forms.ModelForm):
    class Meta:
        model = TourSchedule
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        lat = cleaned_data.get("latitude")
        lng = cleaned_data.get("longitude")
        url = cleaned_data.get("location_url")

        if not lat or not lng:
            raise forms.ValidationError(
                "Please provide latitude and longitude. "
                "Google Maps short links are not supported."
            )

        return cleaned_data
