from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

from api.utils import adjust_to_facility_day


# Custom User with roles
class User(AbstractUser):
    ROLES = (
        ("admin", "Ministry Admin"),
        ("health_worker", "Health Worker"),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    facility = models.ForeignKey(
        "Facility", on_delete=models.SET_NULL, null=True, blank=True
    )


class Facility(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)
    ward = models.CharField(max_length=100)
    lga = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    reg_counter = models.PositiveIntegerField(default=0)  # For sequential child IDs

    def __str__(self):
        return f"{self.name} - {self.code}"


class Child(models.Model):
    uid = models.CharField(max_length=50, unique=True, editable=False)
    full_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(
        max_length=50, choices=[("home", "Home"), ("facility", "Facility")]
    )
    caregiver_name = models.CharField(max_length=255)
    caregiver_contact = models.CharField(max_length=20)
    caregiver_address = models.TextField()
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        creating = self.pk is None
        if not self.uid:
            self.facility.reg_counter += 1
            self.facility.save()
            self.uid = f"{self.facility.state[:2].upper()}{self.facility.lga[:2].upper()}{self.facility.code}{self.facility.reg_counter:04d}"
        super().save(*args, **kwargs)

        if creating:
            self.generate_vaccination_schedule()

    def generate_vaccination_schedule(self):
        from .models import VaccineMaster, Vaccination
        import datetime

        vaccines = VaccineMaster.objects.all().order_by("order")
        for v in vaccines:
            scheduled = self.date_of_birth + datetime.timedelta(days=v.interval_days)
            scheduled = adjust_to_facility_day(scheduled, self.facility)

            Vaccination.objects.create(child=self, vaccine=v, scheduled_date=scheduled)


class VaccineMaster(models.Model):
    name = models.CharField(max_length=50)  # e.g., OPV, Penta, BCG
    dose_number = models.PositiveIntegerField(default=1)  # e.g., 1 for OPV1, 2 for OPV2
    interval_days = models.PositiveIntegerField()  # days after birth
    order = models.PositiveIntegerField()  # sequence across all vaccines

    class Meta:
        unique_together = ("name", "dose_number")
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} Dose {self.dose_number}"


class Vaccination(models.Model):
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="vaccinations"
    )
    vaccine = models.ForeignKey(VaccineMaster, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("scheduled", "Scheduled"), ("given", "Given"), ("missed", "Missed")],
        default="scheduled",
    )
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    health_worker = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    geo_lat = models.FloatField(null=True, blank=True)
    geo_long = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("child", "vaccine")


class SMSLog(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=[("sent", "Sent"), ("failed", "Failed")]
    )


class FacilityVaccinationDay(models.Model):
    DAYS = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="vaccination_days"
    )
    day_of_week = models.IntegerField(choices=DAYS)

    class Meta:
        unique_together = ("facility", "day_of_week")
        ordering = ["day_of_week"]

    def __str__(self):
        return f"{self.facility.name} - {self.get_day_of_week_display()}"
