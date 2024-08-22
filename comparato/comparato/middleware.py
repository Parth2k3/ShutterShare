from django.shortcuts import redirect
from django.conf import settings

class Handle403Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 403:
            return redirect(settings.LOGIN_URL)
        return response
