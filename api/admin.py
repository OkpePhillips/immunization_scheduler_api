from django.contrib import admin
from .models import (
    Facility,
    User,
    Child,
    VaccineMaster,
    Vaccination,
    SMSLog,
    FacilityVaccinationDay,
)


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "location", "contact")
    search_fields = ("name", "location")


@admin.register(FacilityVaccinationDay)
class FacilityVaccinationDayAdmin(admin.ModelAdmin):
    list_display = ("id", "facility", "day_of_week")
    list_filter = ("day_of_week",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "facility",
    )
    search_fields = ("username", "first_name", "last_name", "email")
    list_filter = ("role", "facility")


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "sex",
        "date_of_birth",
        "caregiver_name",
        "caregiver_contact",
        "facility",
    )
    search_fields = ("full_name", "caregiver_name", "caregiver_contact")
    list_filter = ("sex", "facility")


@admin.register(VaccineMaster)
class VaccineMasterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "dose_number", "interval_days", "order")
    list_filter = ("name",)
    ordering = ("order",)


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "child",
        "vaccine",
        "scheduled_date",
        "status",
        "actual_date",
        "health_worker",
    )
    list_filter = ("status", "scheduled_date", "vaccine")
    search_fields = ("child__full_name", "vaccine__name")


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ("id", "child", "message", "status", "sent_at")
    list_filter = ("status", "sent_at")
    search_fields = ("child__full_name", "message")
