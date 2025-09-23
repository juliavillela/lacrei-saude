from rest_framework import viewsets

from .models import Professional
from .serializers import ProfessionalSerializer


class ProfessionalViewSet(viewsets.ModelViewSet):
    serializer_class = ProfessionalSerializer
    queryset = Professional.objects.all()
