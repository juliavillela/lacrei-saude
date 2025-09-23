from django.db import models


class Address(models.Model):
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    complement = models.CharField(max_length=50, blank=True, null=True)
    neighborhood = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=20)

    class Meta:
        abstract = True

    def formatted_address(self):
        complement = f" {self.complement}" if self.complement else ""
        street_part = f"{self.street}, {self.number} {complement}"
        city_part = f"{self.neighborhood}, {self.city}, {self.state}"
        return f"{street_part} - {city_part}. CEP:{self.zipcode}"


class Professional(Address):
    class ProfessionChoices(models.TextChoices):
        GENERAL_PRACTITIONER = "CLINICO_GERAL", "Clínico Geral"
        DERMATOLOGIST = "DERMATOLOGISTA", "Dermatologista"
        GYNECOLOGIST = "GINECOLOGISTA", "Ginecologista"
        PEDIATRICIAN = "PEDIATRA", "Pediatra"
        CARDIOLOGIST = "CARDIOLOGISTA", "Cardiologista"
        PSYCHOLOGIST = "PSICOLOGO", "Psicólogo"
        ORTHOPEDIST = "ORTOPEDISTA", "Ortopedista"
        ENDOCRINOLOGIST = "ENDOCRINOLOGISTA", "Endocrinologista"
        NEUROLOGIST = "NEUROLOGISTA", "Neurologista"
        DENTIST = "DENTISTA", "Dentista"
        # Lista ilustrativa: mais profissões e especialidades podem ser adicionadas.

    name = models.CharField(verbose_name="Nome Social", max_length=255)
    profession = models.CharField(
        verbose_name="Profissão", max_length=50, choices=ProfessionChoices.choices
    )
    phone = models.CharField(verbose_name="Telefone", max_length=20)
    email = models.EmailField(verbose_name="Email", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
