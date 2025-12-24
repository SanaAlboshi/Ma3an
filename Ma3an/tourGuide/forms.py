from django import forms

class TourAnnouncementForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Type your announcement here...', 'rows': 3}),
        label='Announcement',
        max_length=1000
    )
