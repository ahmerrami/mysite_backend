# serializers.py
from rest_framework import serializers
from .models import Omra

class OmraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Omra
        fields = '__all__'