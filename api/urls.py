from django.urls import path
from . import views

urlpatterns = [
    # Facility
    path("facilities/", views.list_facilities),
    path("facilities/add/", views.add_facility),
    # Users
    path("users/", views.list_users),
    path("users/me/", views.users_me),
    path("users/add/", views.add_user),
    # Children & Vaccinations
    path("children/register/", views.register_child),
    path("children/<int:child_id>/vaccinations/", views.child_vaccinations),
    path("reports/compliance/", views.compliance_rate, name="compliance_rate"),
    path("reports/defaulters/", views.defaulters, name="defaulters"),
    path(
        "reports/dropout_rate/<str:vaccine_name>/",
        views.dropout_rate,
        name="dropout_rate",
    ),
    path("reports/dropout_rates/", views.dropout_rates, name="dropout_rates"),
    # Vaccination update
    path("vaccinations/<int:vac_id>/update/", views.update_vaccination),
    # SMS
    path("children/<int:child_id>/send-sms/", views.send_sms),
]
