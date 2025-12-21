from django.utils import timezone
from traveler.models import TravelerPayment

def get_active_join(traveler):
    today = timezone.now().date()

    return TravelerPayment.objects.filter(
        traveler=traveler,
        status="paid",
        tour__start_date__lte=today,
        tour__end_date__gte=today
    ).select_related("tour").first()
