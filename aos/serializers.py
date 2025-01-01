# serializers.py
from rest_framework import serializers
from .models import AO

class AOSerializer(serializers.ModelSerializer):
    class Meta:
        model = AO
        fields = '__all__'