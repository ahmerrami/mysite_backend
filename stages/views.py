#from rest_framework import generics
#from .models import Stage
#from .serializers import StageSerializer

#class StageCreateAPIView(generics.CreateAPIView):
    #queryset = Stage.objects.all()
    #serializer_class = StageSerializer

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ville, Periode
from .serializers import VilleSerializer, PeriodeSerializer, StageSerializer

class VilleListAPIView(generics.ListAPIView):
    serializer_class = VilleSerializer

    def get_queryset(self):
        # Filter Ville instances where 'active' field is True
        return Ville.objects.filter(active=True)

class PeriodeListAPIView(generics.ListAPIView):
    serializer_class = PeriodeSerializer
    def get_queryset(self):
        # Filter Periode instances where 'active' field is True
        return Periode.objects.filter(active=True)

class StageCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = StageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)