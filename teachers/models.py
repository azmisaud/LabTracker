from django.db import models


class Teacher(models.Model):
    """
    Model representing a teacher.

    This model stores basic information about a teacher, including their name.
    """

    name = models.CharField(
        max_length=100,
        help_text="Full name of the teacher. Maximum 100 characters."
    )

    def __str__(self):
        """
        Returns a string representation of the Teacher instance.

        This is typically the value of the 'name' field.

        Returns:
            str: The name of the teacher.
        """
        return self.name

