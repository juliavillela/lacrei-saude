import datetime
from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from professionals.models import Professional

from .models import Appointment

class AppointmentApiTest(APITestCase):
    def setUp(self):
        self.professional = Professional.objects.create(
            name="Alice dos Santos",
            profession=Professional.ProfessionChoices.GENERAL_PRACTITIONER,
            street="Rua das Couves",
            number="123",
            complement="Ap. 4",
            neighborhood="Centro",
            city="Rio de Janeiro",
            state="RJ",
            zipcode="12345678",
            phone="2111112222",
            email="alice@example.com",
        )

        self.time = timezone.now() + datetime.timedelta(days=1)

        self.appointment = Appointment.objects.create(
            professional=self.professional, scheduled_at=self.time
        )

        self.list_url = reverse("appointment-list")
        self.detail_url = reverse("appointment-detail", args=[self.appointment.id])

    def test_list_appointments(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        first_id = response.data[0]["professional"]["id"]
        self.assertEqual(first_id, self.professional.id)

    def test_retrieve_professional(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_id = response.data["professional"]["id"]
        self.assertEqual(response_id, self.professional.id)

        # Read only fields are included
        self.assertIn("name", response.data["professional"])
        self.assertIn("profession", response.data["professional"])

        # Write only fields are not included
        self.assertNotIn("professional_id", response.data)

    def test_create_appointment(self):
        now = timezone.now()
        tomorrow = now + datetime.timedelta(days=1)

        data = {
            "professional_id": self.professional.id,
            "scheduled_at": tomorrow.isoformat(),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)
        self.assertEqual(Appointment.objects.last().professional, self.professional)

    def test_create_appointment_rejects_scheduled_at_in_the_past(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)

        data = {
            "professional_id": self.professional.id,
            "scheduled_at": yesterday.isoformat(),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_create_appointment_rejects_double_booking(self):
        data = {
            "professional_id": self.professional.id,
            "scheduled_at": self.time.isoformat(),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_create_appointment_rejects_non_existing_id(self):
        data = {"professional_id": 5, "scheduled_at": self.time.isoformat()}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_update_appointment(self):
        data = {"scheduled_at": "2025-10-01T08:00:00Z"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(
            self.appointment.scheduled_at,
            datetime.datetime.fromisoformat("2025-10-01T08:00:00Z"),
        )

    def test_delete_appointment(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.count(), 0)
