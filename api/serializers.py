from rest_framework import serializers
from .models import (
    Facility,
    FacilityVaccinationDay,
    User,
    Child,
    VaccineMaster,
    Vaccination,
    SMSLog,
)


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "facility"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = "__all__"
        read_only_fields = ["uid", "created_at", "last_updated"]


class VaccineMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineMaster
        fields = "__all__"


class VaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccination
        fields = "__all__"
        read_only_fields = ["last_updated", "health_worker", "scheduled_date"]


class FacilityVaccinationDaySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = FacilityVaccinationDay
        fields = ["id", "facility", "day_of_week", "day_name"]


class SMSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSLog
        fields = "__all__"
