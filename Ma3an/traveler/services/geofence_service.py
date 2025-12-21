import math
from agency.models import TourSchedule
from traveler.services.geofence_events import record_event_if_changed
from accounts.services.notification_service import notify_user

def is_inside_geofence(lat1, lng1, lat2, lng2, radius):
    R = 6371000
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2 - lat1))
    dlambda = math.radians(float(lng2 - lng1))

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )
    distance = 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return distance <= radius, distance


def check_geofences_and_notify_users(current_location, traveler, tour):
    alerts = []

    schedules = TourSchedule.objects.filter(tour=tour, geofence__is_active=True).select_related("geofence")

    for schedule in schedules:
        geofence = schedule.geofence

        inside, distance = is_inside_geofence(
            current_location.latitude,
            current_location.longitude,
            schedule.latitude,
            schedule.longitude,
            geofence.radius_meters
        )

        event = record_event_if_changed(
            traveler=traveler,
            geofence=geofence,
            inside=inside
        )

        if event and event.event_type == "exit" and geofence.trigger_on_exit:

            notify_user(
            user=traveler.user,
            event=event,
            message="You moved away from the activity location. Please return."
            )

            notify_user(
                user=schedule.tour.tour_guide.user,
                event=event,
                message=f"{traveler.user.get_full_name()} moved away from the activity location."
            )

            alerts.append({
                "schedule": schedule,
                "distance": distance
            })

    return alerts
