from django import forms

from accounts.models import Agency
from agency.models import Subscription


class AgencyApprovalForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ["approval_status", "rejection_reason"]


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = [
            "subscriptionType",
            "price",
            "tours_limit",
            "supervisors_limit",
            "travelers_limit",
        ]
