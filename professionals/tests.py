from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Professional


class ProfessionalApiTest(APITestCase):
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
        self.list_url = reverse("professional-list")
        self.detail_url = reverse("professional-detail", args=[self.professional.id])

    def test_list_professionals(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Alice dos Santos")

    def test_retrieve_professional(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Alice dos Santos")

        # Read only fields are included
        self.assertIn("address", response.data)
        self.assertIn("contact", response.data)

        # Write only fields are not included
        write_only_fields = [
            "street",
            "number",
            "complement",
            "neighborhood",
            "city",
            "state",
            "zipcode",
            "phone",
            "email",
        ]
        for field in write_only_fields:
            self.assertNotIn(field, response.data)

    def test_create_professional(self):
        data = {
            "name": "João da Silva ",
            "profession": "PEDIATRA",
            "street": "Rua das Couves",
            "number": "456",
            "complement": "",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zipcode": "87654-321",
            "phone": "(11)93333-4444",
            "email": "Joao@example.com ",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Professional.objects.count(), 2)
        created_professional = Professional.objects.last()
        
        # Make sure fields were normalized and cleaned
        self.assertEqual(created_professional.name, "João da Silva")
        self.assertEqual(created_professional.phone, "11933334444")
        self.assertEqual(created_professional.zipcode, "87654321")
        self.assertEqual(created_professional.email, "joao@example.com")

    def test_create_professional_rejects_phone_too_short(self):
        data = {
            "name": "João da Silva",
            "profession": "PEDIATRA",
            "street": "Rua das Couves",
            "number": "456",
            "complement": "",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zipcode": "87654-321",
            "phone": "93333-4444",
            "email": "joao@example.com",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Professional.objects.count(), 1)

    def test_create_professional_rejects_phone_too_long(self):
        data = {
            "name": "João da Silva",
            "profession": "PEDIATRA",
            "street": "Rua das Couves",
            "number": "456",
            "complement": "",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zipcode": "87654-321",
            "phone": "(11)93333-44445",
            "email": "joao@example.com",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Professional.objects.count(), 1)

    def test_create_professional_rejects_zip_code_too_long(self):
        data = {
            "name": "João da Silva",
            "profession": "PEDIATRA",
            "street": "Rua das Couves",
            "number": "456",
            "complement": "",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zipcode": "87654-3214",
            "contact_phone": "(11)93333-4444",
            "contact_email": "joao@example.com",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Professional.objects.count(), 1)

    def test_update_professional(self):
        data = {"profession": "PSICOLOGO"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.professional.refresh_from_db()
        self.assertEqual(self.professional.profession, "PSICOLOGO")

    def test_delete_professional(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Professional.objects.count(), 0)
