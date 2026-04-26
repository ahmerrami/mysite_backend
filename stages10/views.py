from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ville, Periode, Stage, Candidat, ValidationCode, Candidature
from .serializers import VilleSerializer, PeriodeSerializer, StageSerializer, CandidatSerializer, ValidationCodeSerializer, CandidatureSerializer
from django.core.mail import send_mail
from django.conf import settings
import random

class VilleViewSet(viewsets.ModelViewSet):
    queryset = Ville.objects.all()
    serializer_class = VilleSerializer

class PeriodeViewSet(viewsets.ModelViewSet):
    queryset = Periode.objects.all()
    serializer_class = PeriodeSerializer

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer

class CandidatViewSet(viewsets.ModelViewSet):
    queryset = Candidat.objects.all()
    serializer_class = CandidatSerializer

    # Nettoyage automatique retiré : géré par la commande management/commands

    @action(detail=True, methods=['post'])
    def send_email_code(self, request, pk=None):
        candidat = self.get_object()
        code = str(random.randint(100000, 999999))
        ValidationCode.objects.create(candidat=candidat, code=code, type='email')
        from_email = getattr(settings, 'AUTHEMAIL_EMAIL_HOST_USER', getattr(settings, 'AUTHEMAIL_EMAIL_HOST_USER', 'noreply@exemple.com'))
        send_mail('Code de validation', f'Votre code : {code}', from_email, [candidat.email])
        return Response({'detail': 'Code envoyé par email.'})


    @action(detail=True, methods=['post'])
    def validate_code(self, request, pk=None):
        from django.utils import timezone
        from datetime import timedelta
        candidat = self.get_object()
        code = request.data.get('code')
        type_ = request.data.get('type')
        try:
            code_obj = ValidationCode.objects.filter(candidat=candidat, code=code, type=type_, is_valid=True).latest('created_at')
        except ValidationCode.DoesNotExist:
            return Response({'detail': 'Code invalide.'}, status=400)
        now = timezone.now()
        if now - code_obj.created_at > timedelta(minutes=30):
            # Supprimer le candidat et ses codes
            candidat.delete()
            return Response({'detail': 'Code expiré, inscription annulée.'}, status=400)
        code_obj.is_valid = False
        code_obj.save()
        if type_ == 'email':
            candidat.email_valide = True
        elif type_ == 'sms':
            candidat.telephone_valide = True
        candidat.save()
        return Response({'detail': 'Code validé.'})

class CandidatureViewSet(viewsets.ModelViewSet):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer
    def create(self, request, *args, **kwargs):
        candidat_id = request.data.get('candidat')
        try:
            candidat = Candidat.objects.get(id=candidat_id)
        except Candidat.DoesNotExist:
            return Response({'detail': 'Candidat introuvable.'}, status=400)
        if not candidat.email_valide:
            return Response({'detail': "L'email n'a pas été validé."}, status=400)
        return super().create(request, *args, **kwargs)
