from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewset(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["professional"]
