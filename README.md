# Immunization Scheduling API

This API is built using the **Django REST Framework (DRF)** to provide a robust and scalable solution for managing immunization scheduling, user roles, facility management, and automated notifications. It's designed for healthcare providers to efficiently track and manage their immunization programs.

## Features

- **User Management**: Securely handle user creation, authentication, and profiles with a clear separation of roles.
- **Facility Management**: Register and manage multiple healthcare facilities, linking them to specific users.
- **Role-Based Access Control (RBAC)**: Implement fine-grained permissions using DRF's built-in system to restrict access to specific actions based on a user's role (e.g., `Admin`, `Scheduler`, `Parent`).
- **Child Registration**: Maintain a comprehensive database of children, linking them to their respective parents or guardians.
- **Immunization Scheduling**: Create, view, update, and delete immunization appointments. The system can be configured to manage a complete vaccination schedule.
- **SMS Notifications**: Integrate with a third-party SMS service (e.g., Twilio) to send automated reminders and updates to parents/guardians.

---

## Technology Stack

- **Backend Framework**: [Django](https://www.djangoproject.com/)
- **API Framework**: [Django REST Framework (DRF)](https://www.django-rest-framework.org/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **SMS Service**: [Twilio](https://www.twilio.com/) 

---

## API Endpoints

The API follows a RESTful design, using DRF's powerful `ModelViewSet` and `router` conventions for consistent and predictable endpoints.

### Users

- `POST /api/users/`: Create a new user account.
- `GET /api/users/`: Retrieve a list of all users.
- `GET /api/users/{id}/`: Retrieve details for a specific user.
- `PUT /api/users/{id}/`: Update a user's details.
- `DELETE /api/users/{id}/`: Delete a user account.

### Facilities

- `POST /api/facilities/`: Create a new healthcare facility.
- `GET /api/facilities/`: List all registered facilities.
- `GET /api/facilities/{id}/`: Retrieve details of a specific facility.
- `PUT /api/facilities/{id}/`: Update facility information.
- `DELETE /api/facilities/{id}/`: Delete a facility record.

### Children

- `POST /api/children/`: Register a new child.
- `GET /api/children/`: List all registered children.
- `GET /api/children/{id}/`: Retrieve details for a specific child.
- `PUT /api/children/{id}/`: Update a child's information.
- `DELETE /api/children/{id}/`: Delete a child's record.

### Appointments

- `POST /api/appointments/`: Schedule a new immunization appointment.
- `GET /api/appointments/`: View all appointments.
- `GET /api/appointments/{id}/`: Retrieve a single appointment's details.
- `PUT /api/appointments/{id}/`: Reschedule or update an appointment.
- `DELETE /api/appointments/{id}/`: Cancel an appointment.

### SMS Notifications

- `POST /api/notifications/sms/`: Manually send an SMS notification.
  *Note: Automated notifications are triggered by certain events, such as appointment creation or updates.*

---

