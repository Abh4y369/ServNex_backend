from django.contrib.auth.backends import BaseBackend
from users.models import User
import logging

logger = logging.getLogger(__name__)

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"=== AUTHENTICATION ATTEMPT ===")
        print(f"username parameter: {username}")
        print(f"password parameter: {'[PROVIDED]' if password else '[MISSING]'}")
        print(f"kwargs: {kwargs}")
        
        email = kwargs.get('email') or username
        print(f"Extracted email: {email}")
        
        if not email or not password:
            print("FAILED: Missing email or password")
            return None
            
        try:
            user = User.objects.get(email=email)
            print(f"User found: {user.email}, ID: {user.id}")
            
            password_valid = user.check_password(password)
            print(f"Password check result: {password_valid}")
            
            if password_valid:
                print("SUCCESS: Authentication passed")
                return user
            else:
                print("FAILED: Password check failed")
                
        except User.DoesNotExist:
            print(f"FAILED: No user found with email: {email}")
            return None
            
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None