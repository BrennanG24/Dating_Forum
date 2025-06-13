from django.utils.timezone import now
from users.models import UserProfile
from datetime import timedelta

class OnlineStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.is_online = True
            profile.last_seen = now()
            profile.save()
        
        response = self.get_response(request)
        return response

    def process_request(self, request):
        if request.user.is_authenticated:
            # Set user to offline if last activity was more than 5 minutes ago
            profile = UserProfile.objects.get(user=request.user)
            if now() - profile.last_seen > timedelta(minutes=5):
                profile.is_online = False
                profile.save()
        return None 