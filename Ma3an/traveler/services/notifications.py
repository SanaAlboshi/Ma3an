def notify_traveler(traveler, schedule, distance):
    print(
        f"Traveler {traveler} is {int(distance)}m away from {schedule.activity_title}"
    )

def notify_tourguide(traveler, schedule, distance):
    print(
        f"ALERT: {traveler} left geofence of {schedule.activity_title}"
    )