from rest_framework import generics
from .models import AO
from .serializers import AOSerializer

class AOListAPIView(generics.ListAPIView):
    serializer_class = AOSerializer

    def get_queryset(self):
        # Filter AO instances where 'isActive' field is True
        return AO.objects.filter(isActive=True)