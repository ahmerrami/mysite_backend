# fournisseurs/middleware.py
from django.http import HttpResponseForbidden
from django.conf import settings
from core.middleware import CurrentUserMiddleware

class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Liste des IPs à bloquer (BLOCKED_IPS dans settings.py)
        self.blocked_ips = getattr(settings, 'BLOCKED_IPS', [])

    def __call__(self, request):
        client_ip = self.get_client_ip(request)

        # Si l'IP est dans la liste noire, bloquer l'accès
        if client_ip in self.blocked_ips:
            return HttpResponseForbidden("Accès refusé : votre adresse IP est bloquée.")

        return self.get_response(request)

    def get_client_ip(self, request):
        """
        Récupère l'IP réelle du client, même derrière un proxy.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()  # Prend la première IP si plusieurs
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
