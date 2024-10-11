from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from faculty.models import Faculty  # Import your Faculty model
from django.contrib.auth.hashers import check_password


class FacultyBackend(BaseBackend):
    """
    Custom authentication backend that allows Faculty members to log in using
    their username and password.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Attempt to find the faculty member by username
            faculty = Faculty.objects.get(username=username)

            # Check if the password is correct
            if faculty and check_password(password, faculty.password):
                return faculty
        except Faculty.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Faculty.objects.get(pk=user_id)
        except Faculty.DoesNotExist:
            return None
