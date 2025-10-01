from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Professional

User = get_user_model()


class ProfessionalApiTest(APITestCase):
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
        self.write_only_fields = [
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
        self.read_only_fields = ["address", "contact"]

        self.list_url = reverse("professional-list")
        self.detail_url = reverse("professional-detail", args=[self.professional.id])

    def make_professional_data(self, **overrides):
        base = {
            "name": "João da Silva",
            "profession": "PEDIATRA",
            "street": "Rua das Couves",
            "number": "456",
            "complement": "",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zipcode": "87654-321",
            "phone": "(11)93333-4444",
            "email": "joao@example.com",
        }
        base.update(overrides)
        return base

    def test_list_professionals(self):
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
        for field in self.read_only_fields:
            self.assertIn(field, item)
        for field in self.write_only_fields:
            self.assertNotIn(field, item)

        self.assertEqual(item["name"], "Alice dos Santos")

    def test_retrieve_professional(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Alice dos Santos")

        for field in self.read_only_fields:
            self.assertIn(field, response.data)

        for field in self.write_only_fields:
            self.assertNotIn(field, response.data)

    def test_retrieve_professional_not_found(self):
        url = reverse("professional-detail", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_professional(self):
        data = self.make_professional_data(
            name=" João da Silva ",
            phone="(11)93333-4444 ",
            zipcode="87654-321 ",
            email="Joao@example.com ",
        )
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Professional.objects.count(), 2)
        created_professional = Professional.objects.last()

        # Make sure fields were normalized and cleaned
        self.assertEqual(created_professional.name, "João da Silva")
        self.assertEqual(created_professional.phone, "11933334444")
        self.assertEqual(created_professional.zipcode, "87654321")
        self.assertEqual(created_professional.email, "joao@example.com")

    def test_create_professional_rejects_missing_required_fields(self):
        data = self.make_professional_data(
            name="", profession="", email="", complement=""
        )
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("profession", response.data)
        self.assertIn("email", response.data)
        self.assertNotIn("complement", response.data)  # Not required
        self.assertEqual(Professional.objects.count(), 1)

    def test_create_professional_rejects_invalid_profession(self):
        data = self.make_professional_data(profession="INVALID")
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profession", response.data)

    def test_create_professional_rejects_phone_too_short(self):
        data = self.make_professional_data(phone="(11)9333-444")
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Professional.objects.count(), 1)

    def test_create_professional_rejects_phone_too_long(self):
        data = self.make_professional_data(phone="(11)93333-44445")
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Professional.objects.count(), 1)

    def test_create_professional_rejects_zip_code_too_long(self):
        data = self.make_professional_data(zipcode="87654-3218")
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Professional.objects.count(), 1)

    def test_create_professional_rejects_zip_code_too_short(self):
        data = self.make_professional_data(zipcode="87654-32")
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Professional.objects.count(), 1)

    def test_create_professional_rejects_existing_email(self):
        data = self.make_professional_data(email=self.professional.email)
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Professional.objects.count(), 1)

    def test_update_professional(self):
        data = {"profession": "PSICOLOGO"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.professional.refresh_from_db()
        self.assertEqual(self.professional.profession, "PSICOLOGO")

    def test_update_professional_with_no_data_changes_nothing(self):
        response = self.client.patch(self.detail_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.professional.refresh_from_db()
        original_data = {
            "name": "Alice dos Santos",
            "profession": Professional.ProfessionChoices.GENERAL_PRACTITIONER,
            "street": "Rua das Couves",
            "number": "123",
            "complement": "Ap. 4",
            "neighborhood": "Centro",
            "city": "Rio de Janeiro",
            "state": "RJ",
            "zipcode": "12345678",
            "phone": "2111112222",
            "email": "alice@example.com",
        }
        for field, value in original_data.items():
            self.assertEqual(getattr(self.professional, field), value)

    def test_update_professional_rejects_empty_required_field(self):
        data = {"name": ""}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.professional.refresh_from_db()
        self.assertEqual(self.professional.name, "Alice dos Santos")

    def test_update_professional_not_found(self):
        url = reverse("professional-detail", args=[999])
        data = {"profession": "PSICOLOGO"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_professional_rejects_invalid_profession(self):
        data = {"profession": "INVALID"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.professional.refresh_from_db()
        self.assertEqual(
            self.professional.profession,
            Professional.ProfessionChoices.GENERAL_PRACTITIONER,
        )

    def test_update_professional_rejects_existing_email(self):
        repeated_email = "repeated@email.com"
        other_professional = self.make_professional_data(email=repeated_email)
        Professional.objects.create(**other_professional)
        data = {"email": repeated_email}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.professional.refresh_from_db()
        self.assertEqual(self.professional.email, "alice@example.com")
        
    def test_full_update_professional(self):
        data = self.make_professional_data(
            name=" Maria Oliveira ",
            phone="(21) 99999-8888 ",
            zipcode="12345-678 ",
            email="  MARIA@EXAMPLE.COM  ",
            )
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.professional.refresh_from_db()
        self.assertEqual(self.professional.name, "Maria Oliveira")
        self.assertEqual(self.professional.phone, "21999998888")
        self.assertEqual(self.professional.zipcode, "12345678")
        self.assertEqual(self.professional.email, "maria@example.com")
    
    def test_full_update_professional_requres_all_fields(self):
        data = self.make_professional_data()
        del data["profession"]
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profession", response.data)
        self.professional.refresh_from_db()
        self.assertEqual(
            self.professional.profession,
            Professional.ProfessionChoices.GENERAL_PRACTITIONER,
        )

    def test_full_update_professional_not_found(self):
        url = reverse("professional-detail", args=[999])
        data = self.make_professional_data()
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_professional(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Professional.objects.count(), 0)

    def test_delete_professional_not_found(self):
        url = reverse("professional-detail", args=[999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Professional.objects.count(), 1)

    def test_unauthenticated_access(self):
        self.client.credentials()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
