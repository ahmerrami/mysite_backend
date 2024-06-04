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
    queryset = Ville.objects.all()
    serializer_class = VilleSerializer

class PeriodeListAPIView(generics.ListAPIView):
    queryset = Periode.objects.all()
    serializer_class = PeriodeSerializer

class StageCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = StageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)