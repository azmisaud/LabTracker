import uuid
from datetime import timezone
import requests
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Custom User model that extends Django's AbstractUser to represent a Student.
class Student(AbstractUser):
    """
    Represents a student, extending the AbstractUser model to include additional
    fields such as enrollment number, faculty number, course, semester, and GitHub repository.

    Attributes:
        enrollment_number (str): Unique identifier for each student.
        faculty_number (str): Unique faculty number for each student.
        course (str): The course that the student is enrolled in.
        semester (str): The current semester of the student.
        repo_name (str): The name of the GitHub repository automatically generated based on the course and semester.
        date_of_birth (date): Date of birth of the student.
    """

    enrollment_number = models.CharField(max_length=11, unique=True)
    faculty_number = models.CharField(max_length=15, unique=True)

    # Choices for the course field
    COURSE_CHOICES = [
        ('BCA', 'B.C.A'),
        ('MCA', 'M.C.A'),
        ('MSC', 'M.Sc(C.S & D.F)'),
    ]

    course = models.CharField(max_length=50, choices=COURSE_CHOICES)

    # Choices for the semester field
    SEMESTER_CHOICES = [
        ('1', 'I'),
        ('2', 'II'),
        ('3', 'III'),
        ('4', 'IV'),
        ('5', 'V'),
        ('6', 'VI'),
        ('7', 'VII'),
        ('8', 'VIII'),
    ]

    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)

    # GitHub repository name, automatically generated and non-editable
    repo_name = models.CharField(max_length=50, blank=True, editable=False)

    # Optional field for the date of birth
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        """
        Returns the username of the student as the string representation of the object.

        Returns:
            str: The username of the student.
        """
        return self.username

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to automatically generate the GitHub repository name
        based on the student's course and semester.

        Args:
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if self.course and self.semester:
            semester_number = self.semester
            course_code = self.course
            # Automatically generate the repository name based on course and semester
            self.repo_name = f"{course_code}Lab{semester_number}"

        # Call the parent class's save method to persist the data
        super().save(*args, **kwargs)

    def github_username_exists(self):
        """
        Checks if the student's GitHub username exists using the GitHub API.

        Returns:
            bool: True if the GitHub username exists, False otherwise.
        """
        url = f"https://api.github.com/users/{self.username}"
        response = requests.get(url)
        return response.status_code == 200

    def github_repository_exists(self):
        """
        Checks if the GitHub repository for the student exists using the GitHub API.

        The repository name is constructed based on the student's course and semester.

        Returns:
            bool: True if the GitHub repository exists, False otherwise.
        """
        repo_name = f"{self.course}Lab{self.semester}"
        url = f"https://api.github.com/repos/{self.username}/{repo_name}"
        response = requests.get(url)
        return response.status_code == 200
