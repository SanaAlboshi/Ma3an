from django.db import transaction
from traveler.models import TravelerLocation

def save_traveler_location(traveler, tour, lat, lng, accuracy=None):
    with transaction.atomic():
        TravelerLocation.objects.filter(
            traveler=traveler,
            is_active=True
        ).update(is_active=False)

        return TravelerLocation.objects.create(
            traveler=traveler,
            tour=tour,
            latitude=lat,
            longitude=lng,
            accuracy=accuracy,
            is_active=True
        )
