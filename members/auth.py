from django.contrib.auth.backends import ModelBackend
from .models import Member
        
        
class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Member.objects.get(email=email)
            if user.password == password:
                return user
        except Member.DoesNotExist:
            return None