from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class AuthenticationBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            user = None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
