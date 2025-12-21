from agency.models import GeofenceEvent

def get_last_event(traveler, geofence):
    return GeofenceEvent.objects.filter(
        traveler=traveler,
        geofence=geofence
    ).order_by("-occurred_at").first()


def record_event_if_changed(traveler, geofence, inside):
    """
    inside = True  -> traveler is inside geofence
    inside = False -> traveler is outside geofence
    """

    last_event = get_last_event(traveler, geofence)

    # Enter
    if inside:
        if not last_event or last_event.event_type == "exit":
            return GeofenceEvent.objects.create(
                traveler=traveler,
                geofence=geofence,
                event_type="enter"
            )

    # Exit
    else:
        if not last_event or last_event.event_type == "enter":
            return GeofenceEvent.objects.create(
                traveler=traveler,
                geofence=geofence,
                event_type="exit"
            )

    return None
