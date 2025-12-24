from django.contrib import admin
from .models import Subscription, AgencyPayment, Tour, TourSchedule

@admin.register(TourSchedule)
class TourScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "tour",
        "activity_title",
        "start_time",
        "latitude",
        "longitude",
    )

    fields = (
        "tour",
        "activity_title",
        "start_time",
        "latitude",
        "longitude",
    )


# تسجيل الموديلات لتظهر في لوحة الإدارة
admin.site.register(Subscription)
admin.site.register(AgencyPayment)
admin.site.register(Tour)
admin.site.register(TourSchedule)
