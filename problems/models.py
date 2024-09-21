from django.db import models


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
