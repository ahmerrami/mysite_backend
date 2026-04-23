from rest_framework import serializers
from .models import Ville, Periode, Stage, Candidat, ValidationCode, Candidature

class VilleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ville
        fields = '__all__'

class PeriodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periode
        fields = '__all__'

class StageSerializer(serializers.ModelSerializer):
    periodes = PeriodeSerializer(many=True, read_only=True)
    villes = VilleSerializer(many=True, read_only=True)
    class Meta:
        model = Stage
        fields = '__all__'

class CandidatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidat
        fields = '__all__'

class ValidationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationCode
        fields = '__all__'

class CandidatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = '__all__'
