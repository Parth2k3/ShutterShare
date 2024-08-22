from rest_framework.permissions import BasePermission
from django.shortcuts import redirect
from django.urls import reverse

class CustomIsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False  # Deny access
        return True

    def permission_denied(self, request, view):
        return redirect(reverse('login'))