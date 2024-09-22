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


class TeacherActivity(models.Model):
    """
    Represents a log of a teacher's actions within a specific course and semester.

    Fields:
        teacher (ForeignKey): A reference to the teacher performing the action, linked to the Teacher model.
        action (CharField): Describes the action taken by the teacher (e.g., "created assignment").
        timestamp (DateTimeField): Automatically stores the time when the action was performed.
        course (CharField): The course associated with the teacher's activity, with a maximum length of 15 characters.
        semester (CharField): The semester during which the action occurred, with a maximum length of 15 characters.
        week (CharField): The week during which the action occurred, optional with a maximum length of 15 characters.
        description (TextField): Optional detailed description of the action, providing additional context if needed.

    Meta:
        verbose_name_plural (str): Changes the plural form of the model in the admin interface to "Teacher Activities".

    Methods:
        __str__: Returns a string representing the teacher, the action, and the timestamp.
        save: Overrides the save method to ensure that only the latest 20 activities per teacher are retained.
               Older activities beyond 20 are deleted to limit data storage.
    """
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    course = models.CharField(max_length=15)
    semester = models.CharField(max_length=15)
    week = models.CharField(max_length=15, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Teacher Activities'

    def __str__(self):
        """
        Returns a string representation of the teacher's action, displaying the teacher's name, the action taken,
        and the timestamp of when the action occurred.
        """
        return f"{self.teacher} {self.action} {self.timestamp}"

    def save(self, *args, **kwargs):
        """
        Saves the TeacherActivity instance and ensures only the latest 20 activities for the teacher are retained.
        If the number of activities exceeds 20, the oldest ones are automatically deleted.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().save(*args, **kwargs)

        # Limit the teacher's activity log to the 20 most recent entries
        activities = TeacherActivity.objects.filter(teacher=self.teacher).order_by('-timestamp')
        if activities.count() > 20:
            # Delete older activities, keeping the 20 most recent ones
            for activity in activities[20:]:
                activity.delete()



class WeekLastDate(models.Model):
    """
    Represents the last date for a specific week in a given course and semester.

    Fields:
        course (CharField): The course for which the last date is being tracked. Choices are 'BCA', 'MCA', and 'M.Sc(C.S & D.F)'.
        semester (IntegerField): The semester for which the week belongs.
        week (IntegerField): The week number within the semester.
        last_date (DateField): The last date associated with the specified week.

    Meta:
        unique_together (tuple): Ensures that a specific course, semester, and week combination is unique.

    Methods:
        __str__: Returns a string representation of the course, semester, week number, and the last date.
    """

    COURSE_CHOICES = [
        ('BCA', 'B.C.A'),
        ('MCA', 'M.C.A'),
        ('MSC', 'M.Sc(C.S & D.F)')
    ]

    course = models.CharField(max_length=15, choices=COURSE_CHOICES)
    semester = models.IntegerField()
    week = models.IntegerField()
    last_date = models.DateField()

    class Meta:
        unique_together = ('course', 'semester', 'week')

    def __str__(self):
        """
        Returns a string representation of the course, semester, week, and the corresponding last date.
        """
        return f"{self.course} {self.semester} {self.week} {self.last_date}"
