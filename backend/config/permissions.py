from rest_framework import permissions
from django.conf import settings


class IsADKWorker(permissions.BasePermission):
    """
    Allows access only if a valid ADK_WORKER_SECRET is provided.
    """
    def has_permission(self, request, view):
        # Get the secret key from the request header
        provided_key = request.headers.get('X-ADK-Worker-Secret')
        
        # Get the expected secret key from your .env file
        # Make sure to add ADK_WORKER_SECRET="your-strong-random-secret"
        expected_key = settings.ADK_WORKER_SECRET
        
        if not expected_key:
            # Fail safely if the setting is missing
            return False
            
        return provided_key == expected_key