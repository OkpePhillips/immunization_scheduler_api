from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import render
from django.db.models import F, Min, Max

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Facility, User, Child, VaccineMaster, Vaccination, SMSLog
from .serializers import (
    FacilitySerializer,
    UserSerializer,
    ChildSerializer,
    VaccinationSerializer,
    SMSLogSerializer,
    FacilityVaccinationDaySerializer,
)

# Common auth parameter for Swagger
auth_param = openapi.Parameter(
    "Authorization",
    openapi.IN_HEADER,
    description="Token: Bearer <your_token>",
    type=openapi.TYPE_STRING,
    required=True,
)


# -------------------------------
# Facility Management
# -------------------------------
@swagger_auto_schema(
    method="post",
    operation_summary="Add Facility",
    manual_parameters=[auth_param],
    request_body=FacilitySerializer,
    responses={201: FacilitySerializer, 403: "Unauthorized"},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_facility(request):
    if request.user.role != "admin":
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    serializer = FacilitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    operation_summary="Add Facility Vaccination Day",
    manual_parameters=[auth_param],
    request_body=FacilityVaccinationDaySerializer,
    responses={201: FacilityVaccinationDaySerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_facility_vaccination_day(request):
    serializer = FacilityVaccinationDaySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="List All Facilities",
    manual_parameters=[auth_param],
    responses={200: FacilitySerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_facilities(request):
    facilities = Facility.objects.all()
    serializer = FacilitySerializer(facilities, many=True)
    return Response(serializer.data)


# -------------------------------
# User Management (Admins add workers)
# -------------------------------
@swagger_auto_schema(
    method="post",
    operation_summary="Add User (Admin Only)",
    manual_parameters=[auth_param],
    request_body=UserSerializer,
    responses={201: UserSerializer, 403: "Unauthorized"},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_user(request):
    if request.user.role != "admin":
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="List Users",
    manual_parameters=[auth_param],
    responses={200: UserSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# -------------------------------
# Child Registration & Vaccination Scheduling
# -------------------------------
@swagger_auto_schema(
    method="post",
    operation_summary="Register Child and Auto-Schedule Vaccines",
    manual_parameters=[auth_param],
    request_body=ChildSerializer,
    responses={201: ChildSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_child(request):
    serializer = ChildSerializer(data=request.data)
    if serializer.is_valid():
        child = serializer.save()

        # Auto-generate vaccination schedule
        vaccines = VaccineMaster.objects.all().order_by("order")
        for v in vaccines:
            Vaccination.objects.create(
                child=child,
                vaccine=v,
                scheduled_date=child.date_of_birth + timedelta(days=v.interval_days),
            )

        return Response(ChildSerializer(child).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="Get Child Vaccinations",
    manual_parameters=[auth_param],
    responses={200: VaccinationSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def child_vaccinations(request, child_id):
    child = get_object_or_404(Child, id=child_id)
    vaccinations = Vaccination.objects.filter(child=child)
    serializer = VaccinationSerializer(vaccinations, many=True)
    return Response(serializer.data)


# -------------------------------
# Vaccination Recording
# -------------------------------
@swagger_auto_schema(
    method="patch",
    operation_summary="Update Vaccination Record",
    manual_parameters=[auth_param],
    request_body=VaccinationSerializer,
    responses={200: VaccinationSerializer},
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_vaccination(request, vac_id):
    vaccination = get_object_or_404(Vaccination, id=vac_id)
    serializer = VaccinationSerializer(vaccination, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(health_worker=request.user, last_updated=now())
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# SMS Handling (Trigger Reminder)
# -------------------------------
@swagger_auto_schema(
    method="post",
    operation_summary="Send SMS Reminder",
    manual_parameters=[auth_param],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
        required=[],
    ),
    responses={201: SMSLogSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_sms(request, child_id):
    child = get_object_or_404(Child, id=child_id)
    message = request.data.get(
        "message", f"Reminder: {child.full_name} has an immunization due soon."
    )

    # TODO: integrate real SMS provider (Termii, Twilio, Africa’s Talking)
    sms_status = "sent"  # assume success for now

    sms_log = SMSLog.objects.create(child=child, message=message, status=sms_status)
    return Response(SMSLogSerializer(sms_log).data, status=status.HTTP_201_CREATED)


# ---------- Reporting ----------


@swagger_auto_schema(
    method="get",
    operation_summary="Get Compliance Rate",
    manual_parameters=[auth_param],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"compliance_rate": openapi.Schema(type=openapi.TYPE_NUMBER)},
        )
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def compliance_rate(request):
    """
    Compliance = % of given vaccines that were administered on or before scheduled_date
    """
    total = Vaccination.objects.filter(status="given").count()
    if total == 0:
        return Response({"compliance_rate": 0})

    on_time = Vaccination.objects.filter(
        status="given", actual_date__lte=F("scheduled_date")
    ).count()

    rate = round((on_time / total) * 100, 2)
    return Response({"compliance_rate": rate})


@swagger_auto_schema(
    method="get",
    operation_summary="List Defaulters",
    manual_parameters=[auth_param],
    responses={200: ChildSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def defaulters(request):
    """
    List children who missed at least one vaccine
    """
    child_ids = (
        Vaccination.objects.filter(status="missed")
        .values_list("child_id", flat=True)
        .distinct()
    )
    children = Child.objects.filter(id__in=child_ids)
    serializer = ChildSerializer(children, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    operation_summary="Get Dropout Rate for Vaccine Series",
    manual_parameters=[auth_param],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "series": openapi.Schema(type=openapi.TYPE_STRING),
                "started": openapi.Schema(type=openapi.TYPE_INTEGER),
                "completed": openapi.Schema(type=openapi.TYPE_INTEGER),
                "dropout_rate": openapi.Schema(type=openapi.TYPE_NUMBER),
            },
        )
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dropout_rate(request, vaccine_name: str):
    """
    Dropout = (children who got first dose but not last dose) / (children who got first dose) * 100
    Example: /api/reports/dropout_rate/Penta/
    """
    # Get vaccine series
    vaccines = VaccineMaster.objects.filter(name__icontains=vaccine_name)

    if not vaccines.exists():
        return Response(
            {"error": f"No vaccines found for series '{vaccine_name}'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Find first and last dose in the series
    first_dose = vaccines.aggregate(Min("dose_number"))["dose_number__min"]
    last_dose = vaccines.aggregate(Max("dose_number"))["dose_number__max"]

    if first_dose is None or last_dose is None or first_dose == last_dose:
        return Response(
            {"error": f"Series '{vaccine_name}' does not have multiple doses"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    first_vaccine = vaccines.filter(dose_number=first_dose).first()
    last_vaccine = vaccines.filter(dose_number=last_dose).first()

    started = Vaccination.objects.filter(vaccine=first_vaccine, status="given").count()
    completed = Vaccination.objects.filter(vaccine=last_vaccine, status="given").count()

    if started == 0:
        return Response({"dropout_rate": 0})

    dropout = round(((started - completed) / started) * 100, 2)
    return Response(
        {
            "series": vaccine_name,
            "started": started,
            "completed": completed,
            "dropout_rate": dropout,
        }
    )


@swagger_auto_schema(
    method="get",
    operation_summary="Get All Dropout Rate for Various Vaccines",
    manual_parameters=[auth_param],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "series": openapi.Schema(type=openapi.TYPE_STRING),
                "started": openapi.Schema(type=openapi.TYPE_INTEGER),
                "completed": openapi.Schema(type=openapi.TYPE_INTEGER),
                "dropout_rate": openapi.Schema(type=openapi.TYPE_NUMBER),
            },
        )
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dropout_rates(request):
    response = []
    # Group vaccines by prefix before digits (e.g., Penta1, Penta2 → "Penta")
    vaccine_series = set(VaccineMaster.objects.values_list("name", flat=True))
    prefixes = {name.rstrip("0123456789") for name in vaccine_series}

    for prefix in prefixes:
        doses = VaccineMaster.objects.filter(name__icontains=prefix).order_by("order")
        if doses.count() < 2:
            continue

        first_dose = doses.first()
        last_dose = doses.last()

        first_count = Vaccination.objects.filter(
            vaccine=first_dose, status="given"
        ).count()
        last_count = Vaccination.objects.filter(
            vaccine=last_dose, status="given"
        ).count()

        dropout_rate = None
        if first_count > 0:
            dropout_rate = ((first_count - last_count) / first_count) * 100

        response.append(
            {
                "vaccine_series": prefix,
                "first_dose": first_dose.name,
                "last_dose": last_dose.name,
                "first_count": first_count,
                "last_count": last_count,
                "dropout_rate": dropout_rate,
            }
        )

    return JsonResponse(response, safe=False)
