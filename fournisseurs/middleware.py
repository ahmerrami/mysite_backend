import threading

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
