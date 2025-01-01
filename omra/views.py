from rest_framework import generics
from .models import Omra
from .serializers import OmraSerializer

class OmraListAPIView(generics.ListAPIView):
    serializer_class = OmraSerializer

    def get_queryset(self):
        # Filter Omra instances where 'isActive' field is True
        return Omra.objects.filter(isActive=True)