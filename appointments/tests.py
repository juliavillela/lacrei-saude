import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from professionals.models import Professional

from .models import Appointment

User = get_user_model()


class AppointmentApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass"
        )

        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

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

        self.professional_read_only_fields = ["id", "name", "profession"]
        self.professional_write_only_fields = ["professional_id"]

        self.list_url = reverse("appointment-list")
        self.detail_url = reverse("appointment-detail", args=[self.appointment.id])

    def test_list_appointments(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Pagination fields are present
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

        self.assertIn("results", response.data)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        item = results[0]
        self.assertEqual(item["id"], self.appointment.id)
        
        professional = item["professional"]
        for field in self.professional_read_only_fields:
            self.assertIn(field, professional)

        for field in self.professional_write_only_fields:
            self.assertNotIn(field, professional)

    def test_retrieve_appointment(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        professional = response.data["professional"]
        self.assertEqual(professional["id"], self.professional.id)

        for field in self.professional_read_only_fields:
            self.assertIn(field, professional)

        for field in self.professional_write_only_fields:
            self.assertNotIn(field, professional)

    def test_retrieve_appointment_not_found(self):
        url = reverse("appointment-detail", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_create_appointment_rejects_missing_required_fields(self):
        data = {}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("professional_id", response.data)
        self.assertIn("scheduled_at", response.data)
        self.assertEqual(Appointment.objects.count(), 1)

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
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        data = {"scheduled_at": tomorrow.isoformat()}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(
            self.appointment.scheduled_at,
            tomorrow,
        )

    def test_update_appointment_with_no_data_changes_nothing(self):
        data = {}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.scheduled_at, self.time)
        self.assertEqual(self.appointment.professional, self.professional)

    def test_update_appointment_rejects_empty_required_fields(self):
        data = {"professional_id": ""}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("professional_id", response.data)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.professional, self.professional)

    def test_update_appointment_rejects_non_existing_professional_id(self):
        data = {"professional_id": 999}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.professional, self.professional)

    def test_update_appointment_rejects_scheduled_at_in_the_past(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        data = {"scheduled_at": yesterday.isoformat()}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.scheduled_at, self.time)

    def test_update_appointment_rejects_double_booking(self):
        # Create another appointment at a different time
        another_time = self.time + datetime.timedelta(hours=1)
        Appointment.objects.create(
            professional=self.professional, scheduled_at=another_time
        )
        # Try to update the first appointment to the same time as the second
        data = {"scheduled_at": another_time.isoformat()}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.scheduled_at, self.time)

        # Create an appointment with a different professional at the same time
        another_professional = Professional.objects.create(
            name="Ana Pereira",
            profession=Professional.ProfessionChoices.DERMATOLOGIST,
            street="Rua das Flores",
            number="789",
            complement="Ap. 10",
            neighborhood="Jardim",
            city="São Paulo",
            state="SP",
            zipcode="98765432",
            phone="3199998888",
            email="ana@email.com",
        )
        Appointment.objects.create(
            professional=another_professional, scheduled_at=self.time
        )

        # Try to update the first appointment to the same professional as the second
        data = {"professional_id": another_professional.id}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.professional, self.professional)

    def test_update_appointment_not_found(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        url = reverse("appointment-detail", args=[999])
        data = {"scheduled_at": tomorrow.isoformat()}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_appointment(self):
        other_professional = Professional.objects.create(
            name="Tereza Souza",
            profession=Professional.ProfessionChoices.CARDIOLOGIST,
            street="Rua das Palmeiras",
            number="456",
            complement="Ap. 2",
            neighborhood="Bela Vista",
            city="Curitiba",
            state="PR",
            zipcode="87654321",
            phone="4198887777",
            email="tereza@email.com",
        )        
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        data = {
            "professional_id": other_professional.id,
            "scheduled_at": tomorrow.isoformat(),
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(
            self.appointment.scheduled_at,
            tomorrow,
        )
        self.assertEqual(self.appointment.professional, other_professional)

    def test_full_update_appointment_requires_all_fields(self):
        today = timezone.now() + datetime.timedelta(days=1)
        data = {"scheduled_at": today.isoformat()}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("professional_id", response.data)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.scheduled_at, self.time)
        self.assertEqual(self.appointment.professional, self.professional)
    
    def test_full_update_appointment_not_found(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        url = reverse("appointment-detail", args=[999])
        data = {
            "professional_id": self.professional.id,
            "scheduled_at": tomorrow.isoformat(),
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_appointment(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_delete_appointment_not_found(self):
        url = reverse("appointment-detail", args=[999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_unauthenticated_access(self):
        self.client.credentials()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FilterApointmentByProfessionals(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass"
        )

        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.professional_1 = Professional.objects.create(
            name="Alice dos Santos",
            profession=Professional.ProfessionChoices.GENERAL_PRACTITIONER,
            street="Rua das Couves",
            number="123",
            complement="Ap. 4",
            neighborhood="Centro",
            city="Rio de Janeiro",
            state="RJ",
            zipcode="12345-678",
            phone="211111-2222",
            email="alice@example.com",
        )

        self.professional_2 = Professional.objects.create(
            name="Maria da Silva",
            profession=Professional.ProfessionChoices.GYNECOLOGIST,
            street="Rua das Couves",
            number="123",
            complement="Ap. 7",
            neighborhood="Centro",
            city="Rio de Janeiro",
            state="RJ",
            zipcode="12345-678",
            phone="211111-2222",
            email="maria@example.com",
        )
        today = timezone.now() + datetime.timedelta(hours=1)
        tomorrow = today + datetime.timedelta(days=1)

        self.appointment_1 = Appointment.objects.create(
            professional=self.professional_1, scheduled_at=today.isoformat()
        )
        self.appointment_2 = Appointment.objects.create(
            professional=self.professional_1, scheduled_at=tomorrow.isoformat()
        )
        self.appointment_3 = Appointment.objects.create(
            professional=self.professional_2, scheduled_at=today.isoformat()
        )

    def test_filter_by_professional(self):
        url = reverse("appointment-list") + f"?professional={self.professional_1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        returned_ids = [appointment["id"] for appointment in results]
        self.assertIn(self.appointment_1.id, returned_ids)
        self.assertIn(self.appointment_2.id, returned_ids)
        self.assertNotIn(self.appointment_3.id, returned_ids)
        self.assertEqual(len(returned_ids), 2)

    def test_filter_by_professional_raises_error_for_non_existing_id(self):
        url = reverse("appointment-list") + "?professional=5"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
