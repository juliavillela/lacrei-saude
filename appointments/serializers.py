from django.utils import timezone
from rest_framework import serializers

from professionals.models import Professional
from professionals.serializers import PartialProfessionalSerializer

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    professional_id = serializers.PrimaryKeyRelatedField(
        queryset=Professional.objects.all(), source="professional", write_only=True
    )
    professional = PartialProfessionalSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "professional",
            "scheduled_at",
            "professional_id",
            "created_at",
            "updated_at",
        ]

    def validate_scheduled_at(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Uma consulta não pode ser marcada no passado."
            )
        return value

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        professional = attrs.get("professional") or (
            instance.professional if instance else None
        )
        scheduled_at = attrs.get("scheduled_at") or (
            instance.scheduled_at if instance else None
        )

        qs = Appointment.objects.filter(
            professional=professional, scheduled_at=scheduled_at
        )

        if instance:
            qs = qs.exclude(id=instance.id)

        if qs.exists():
            raise serializers.ValidationError(
                "Esse profissional já possui uma consulta neste horário."
            )

        return attrs
