from django.db import models


class Appointment(models.Model):
    professional = models.ForeignKey(
        to="professionals.Professional",
        verbose_name="Profissional de saúde",
        related_name="appointments",
        on_delete=models.CASCADE,
    )
    scheduled_at = models.DateTimeField(verbose_name="Data e Horário")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        date = self.scheduled_at.date().isoformat()
        time = self.scheduled_at.time().isoformat()
        return f"{self.professional.name} - {date} ({time})"
