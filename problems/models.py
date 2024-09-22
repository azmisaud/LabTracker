from django.db import models
from django.conf import settings
from students.models import Student

class Problem(models.Model):
    """
    A Django model representing a problem assigned to students in a specific course, semester, and week.

    Attributes:
        COURSE_CHOICES (list of tuple): Defines choices for the course field. It contains three courses:
            - 'BCA' for Bachelor of Computer Applications.
            - 'MCA' for Master of Computer Applications.
            - 'MSC' for Master of Science (Cybersecurity & Digital Forensics).

        course (CharField): The course to which the problem belongs. Choices are defined in COURSE_CHOICES.
        semester (IntegerField): The semester number for which the problem is assigned.
        week (IntegerField): The week number of the semester in which the problem is assigned.
        problemNumber (CharField): A unique identifier for the problem within a course, semester, and week.
        description (TextField): A textual description of the problem.
        image (ImageField): An optional image related to the problem, stored in 'problems/static/images/' directory.
                           This field is optional and can be left blank or null.

    Meta:
        constraints (list): Ensures that each problem is unique within the same course, semester, week, and problem number.
            - UniqueConstraint: Ensures that no two problems can share the same course, semester, week, and problemNumber.

    Methods:
        __str__: Returns a string representation of the problem in the format:
                 "<course> - Sem <semester> - Week <week> - <problemNumber>"

    Example:
        A string representation of a problem might be:
        "BCA - Sem 2 - Week 5 - Problem 3"
    """

    COURSE_CHOICES = [
        ('BCA', 'B.C.A'),
        ('MCA', 'M.C.A'),
        ('MSC', 'M.Sc(C.S & D.F)')
    ]

    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    semester = models.IntegerField()
    week = models.IntegerField()
    problemNumber = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='problems/static/images/', blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'semester', 'week', 'problemNumber'], name='unique_problem'),
        ]

    def __str__(self):
        """
        Returns a string representation of the Problem instance for easy identification.

        Example:
            "BCA - Sem 1 - Week 2 - P1"
        """
        return f"{self.course} - Sem {self.semester} - Week {self.week} - {self.problemNumber}"


class ProblemCompletion(models.Model):
    """
    Represents a student's completion status for a specific problem.

    Fields:
        student (ForeignKey): A reference to the student (linked to Django's user model) who has attempted the problem.
        problem (ForeignKey): A reference to the specific problem the student is attempting.
        is_completed (BooleanField): Indicates whether the problem has been completed by the student.
        solution_url (URLField): Optional URL to the solution provided by the student.
        output_image_url (URLField): Optional URL to an image that represents the student's output or solution.

    Meta:
        unique_together (tuple): Ensures that each student can only have one completion record for each problem.

    Methods:
        __str__: Returns a formatted string displaying the student, the problem's week, problem number, and whether it has been completed.
    """
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    solution_url = models.URLField(blank=True, null=True)
    output_image_url = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'problem')

    def __str__(self):
        """
        Returns a string representation of the problem completion status, including the student's username,
        the week of the problem, the problem number, and the completion status.
        """
        return f"{self.student} - {self.problem.week} - {self.problem.problemNumber} - Completed: {self.is_completed}"


from django.db import models


class WeekCommit(models.Model):
    """
    Represents a student's commit information for a specific week.

    Fields:
        student (ForeignKey): A reference to the student making the commit, linked to the Student model.
        week_number (IntegerField): Indicates the week for which the commit is being tracked.
        last_commit_time (DateTimeField): The timestamp of the student's most recent commit for the given week.
        last_commit_hash (CharField): Stores the SHA-1 hash of the last commit, allowing up to 40 characters. This field is optional.

    Meta:
        unique_together (tuple): Ensures that each student can only have one commit entry per week.

    Methods:
        __str__: Returns a string displaying the student's username and the corresponding week number.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    week_number = models.IntegerField()
    last_commit_time = models.DateTimeField(null=True, blank=True)
    last_commit_hash = models.CharField(max_length=40, null=True, blank=True)  # Assuming SHA-1 hash

    class Meta:
        unique_together = ('student', 'week_number')

    def __str__(self):
        """
        Returns a string representation of the student's commit for a specific week,
        displaying the student's username and the week number.
        """
        return f"{self.student.username} - Week {self.week_number}"
