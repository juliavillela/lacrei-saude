from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Professional
from .serializers import ProfessionalSerializer


class ProfessionalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalSerializer
    queryset = Professional.objects.all()
