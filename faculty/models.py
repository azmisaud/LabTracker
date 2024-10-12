from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
from django.conf import settings
from  django.utils import timezone
import uuid

class FacultyManager(BaseUserManager):
    def create_faculty(self,name,**extra_fields):
        if not name:
            raise ValueError('Faculty Name is required')

        first_name=name.split()[1]
        base_username=f"{first_name}amuCS"

        username=base_username.lower()

        count=1

        while Faculty.objects.filter(username=username).exists():
            username=f"{username}amuCS{count}"
            count+=1

        expected_password=f"{first_name}@{settings.TEACHER_PASSWORD_BASE}"

        faculty=self.model(
            name=name,
            username=username,
            is_staff=True,
            **extra_fields
        )

        faculty.set_password(expected_password)
        faculty.save(using=self._db)

        return faculty

    def promote_to_superuser(self,faculty):
        if not isinstance(faculty,Faculty):
            raise ValueError('Faculty must be of type Faculty')

        faculty.is_staff=True
        faculty.is_superuser=True
        faculty.save(using=self._db)
        return faculty



class Faculty(AbstractBaseUser, PermissionsMixin):
    name=models.CharField(max_length=100)
    username=models.CharField(max_length=50,unique=True,editable=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_first_login=models.BooleanField(default=True)

    objects = FacultyManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    groups=models.ManyToManyField(
        'auth.Group',
        related_name='faculty_groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted ',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='faculty_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user_permissions',
    )
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)



class LastDateOfWeek(models.Model):
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


class FacultyActivity(models.Model):
    """
    Represents a log of a faculty member's actions within a specific course and semester.

    Fields:
        faculty (ForeignKey): A reference to the faculty member performing the action, linked to the Faculty model.
        action (CharField): Describes the action taken by the faculty member (e.g., "created assignment").
        timestamp (DateTimeField): Automatically stores the time when the action was performed.
        course (CharField): The course associated with the faculty member's activity, with a maximum length of 15 characters.
        semester (CharField): The semester during which the action occurred, with a maximum length of 15 characters.
        week (CharField): The week during which the action occurred, optional with a maximum length of 15 characters.
        description (TextField): Optional detailed description of the action, providing additional context if needed.

    Meta:
        verbose_name_plural (str): Changes the plural form of the model in the admin interface to "Faculty Activities".

    Methods:
        __str__: Returns a string representing the faculty member, the action, and the timestamp.
        save: Overrides the save method to ensure that only the latest 20 activities per faculty member are retained.
               Older activities beyond 20 are deleted to limit data storage.
    """
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE)  # Changed from 'Teacher' to 'Faculty'
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    course = models.CharField(max_length=15)
    semester = models.CharField(max_length=15)
    week = models.CharField(max_length=15, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Faculty Activities'  # Updated plural name

    def __str__(self):
        """
        Returns a string representation of the faculty member's action, displaying the faculty member's name, the action taken,
        and the timestamp of when the action occurred.
        """
        return f"{self.faculty} {self.action} {self.timestamp}"

    def save(self, *args, **kwargs):
        """
        Saves the FacultyActivity instance and ensures only the latest 20 activities for the faculty member are retained.
        If the number of activities exceeds 20, the oldest ones are automatically deleted.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().save(*args, **kwargs)

        # Limit the faculty member's activity log to the 20 most recent entries
        activities = FacultyActivity.objects.filter(faculty=self.faculty).order_by('-timestamp')
        if activities.count() > 20:
            # Delete older activities, keeping the 20 most recent ones
            for activity in activities[20:]:
                activity.delete()
