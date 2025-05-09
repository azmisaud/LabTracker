from django.core.management.base import BaseCommand
from students.models import Student
from faker import Faker
import random


class Command(BaseCommand):
    help = 'Creates 50 test students for testing purposes'

    def handle(self, *args, **kwargs):
        fake = Faker()
        courses = ['BCA']
        semesters = ['3']

        for i in range(50):
            username = f"student{i}bca"
            password = "testpassword123"
            enrollment_number = f"ENRbca{i:04d}"
            faculty_number = f"FACbca{i:04d}"
            course = random.choice(courses)
            semester = random.choice(semesters)
            dob = fake.date_of_birth(minimum_age=18, maximum_age=25)

            Student.objects.create_user(
                username=username,
                password=password,
                enrollment_number=enrollment_number,
                faculty_number=faculty_number,
                course=course,
                semester=semester,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=dob
            )

        self.stdout.write(self.style.SUCCESS("Successfully created 50 test students"))
