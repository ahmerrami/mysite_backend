# middleware.py
import threading
from django.http import HttpResponseForbidden
from django.conf import settings

class CurrentUserMiddleware:
    _user = threading.local()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        CurrentUserMiddleware._user.value = request.user if request.user.is_authenticated else None
        response = self.get_response(request)
        return response

    @staticmethod
    def get_current_user():
        return getattr(CurrentUserMiddleware._user, "value", None)
    
class RestrictIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', [])

    def __call__(self, request):
        ip = self.get_client_ip(request)
        if ip not in self.allowed_ips:
            return HttpResponseForbidden("Accès interdit : votre adresse IP n'est pas autorisée.")
        return self.get_response(request)

    def get_client_ip(self, request):
        # PythonAnywhere fournit souvent l'IP via REMOTE_ADDR
        # Si tu es derrière un proxy (ex: nginx), adapte ici
        return request.META.get('REMOTE_ADDR')

