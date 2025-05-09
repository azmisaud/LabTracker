from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from instructor.models import Instructor
from django.contrib.auth.hashers import check_password

class InstructorBackend(BaseBackend):
    """
    Custom authentication backend that allows Instructors to log in using
    their username and password.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Attempt to find the instructor by username
            instructor = Instructor.objects.get(username=username)

            # Check if the password is correct
            if instructor and check_password(password, instructor.password):
                return instructor
        except Instructor.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Instructor.objects.get(pk=user_id)
        except Instructor.DoesNotExist:
            return None 