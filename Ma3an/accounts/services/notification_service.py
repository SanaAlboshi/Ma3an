from accounts.models import Notification

def notify_user(user, event, message):
    """
    Create a notification for a user based on a geofence event.
    """
    return Notification.objects.create(
        user=user,
        event=event,
        message=message
    )