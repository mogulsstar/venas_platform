"""
Middleware for the monitor app.
"""

import time
from django.utils import timezone

from .models import UserRequest


class RequestMonitoringMiddleware:
    """
    Middleware to monitor user requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start timer
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # End timer
        end_time = time.time()
        
        # Calculate response time
        response_time = end_time - start_time
        
        # Skip monitoring for static files and admin media
        if not (request.path.startswith('/static/') or request.path.startswith('/media/')):
            # Create a record of the request
            try:
                UserRequest.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    path=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    response_time=response_time
                )
            except Exception:
                # Don't let monitoring errors affect the response
                pass
        
        return response
    
    def get_client_ip(self, request):
        """
        Get the client's IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
