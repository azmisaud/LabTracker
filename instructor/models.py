from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission
from django.conf import settings
from django.utils import timezone
import uuid
from students.models import Student

class InstructorManager(BaseUserManager):
    def create_instructor(self, name, **extra_fields):
        if not name:
            raise ValueError('Instructor Name is required')

        first_name = name.split()[1]
        base_username = f"{first_name}amuCS"

        username = base_username.lower()

        count = 1

        while Instructor.objects.filter(username=username).exists():
            username = f"{username}amuCS{count}"
            count += 1

        expected_password = f"{first_name}@{settings.TEACHER_PASSWORD_BASE}"

        instructor = self.model(
            name=name,
            username=username,
            is_staff=True,
            **extra_fields
        )

        instructor.set_password(expected_password)
        instructor.save(using=self._db)

        return instructor

    def create_superuser(self, instructor):
        if not isinstance(instructor, Instructor):
            raise ValueError('Instructor must be of type Instructor')

        instructor.is_staff = True
        instructor.is_superuser = True
        instructor.is_active = True

        all_permissions = Permission.objects.all()
        instructor.user_permissions.set(all_permissions)
        instructor.save(using=self._db)
        return instructor

class Instructor(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_first_login = models.BooleanField(default=True)

    objects = InstructorManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='instructor_groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='instructor_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class SelectedStudent(models.Model):
    instructor = models.ForeignKey('Instructor', on_delete=models.CASCADE, related_name='selected_students')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='selected_by')
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('instructor', 'student')

from problems.models import Problem, ProblemCompletion


class InstructorComment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey('Instructor', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Comment by {self.marked_by} on {self.student.username} - {self.problem}"

class CodeSubmission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    raw_code = models.TextField(blank=True, null=True)
    ai_analysis = models.TextField(blank=True, null=True)
    is_valid = models.BooleanField(default=True)
    reviewed_by = models.ForeignKey('Instructor', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.problem} - Valid: {self.is_valid}"

class InstructorActionLog(models.Model):
    ACTION_CHOICES = [
        ('MARK_RIGHT', 'Marked as Right'),
        ('MARK_WRONG', 'Marked as Wrong and Deleted'),
        ('COMMENTED', 'Commented'),
    ]

    instructor = models.ForeignKey('Instructor', on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.instructor} - {self.action} - {self.student} - {self.problem}"

class CodeReview(models.Model):
    submission=models.OneToOneField(ProblemCompletion, on_delete=models.CASCADE)
    instructor=models.ForeignKey(Instructor, on_delete=models.CASCADE)
    comment=models.TextField(blank=True,null=True)
    is_correct=models.BooleanField(default=False)
    reviewed_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.submission.student.username} - Reviewed by {self.instructor.username}"

# class InstructorActivity(models.Model):
#     """
#     Represents a log of an instructor's actions within the mentoring system.
#     """
#     instructor = models.ForeignKey('Instructor', on_delete=models.CASCADE)
#     action = models.CharField(max_length=100)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     student = models.ForeignKey('students.Student', on_delete=models.CASCADE, null=True, blank=True)
#     description = models.TextField(null=True, blank=True)
#
#     class Meta:
#         verbose_name_plural = 'Instructor Activities'
#
#     def __str__(self):
#         return f"{self.instructor} {self.action} {self.timestamp}"
#
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         # Limit the instructor's activity log to the 20 most recent entries
#         activities = InstructorActivity.objects.filter(instructor=self.instructor).order_by('-timestamp')
#         if activities.count() > 20:
#             for activity in activities[20:]:
#                 activity.delete()
#
# class Mentorship(models.Model):
#     instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='mentorships')
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mentorships')
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
#
#     class Meta:
#         unique_together = ('instructor', 'student')
#
#     def __str__(self):
#         return f"{self.instructor.name} - {self.student.name}"
#
# class CodeReview(models.Model):
#     mentorship = models.ForeignKey(Mentorship, on_delete=models.CASCADE, related_name='code_reviews')
#     repository_url = models.URLField()
#     commit_hash = models.CharField(max_length=100)
#     code_summary = models.TextField(blank=True)
#     rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)], null=True, blank=True)
#     comments = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"Review for {self.mentorship.student.name}'s code"
#
# class CodeSummary(models.Model):
#     code_review = models.OneToOneField(CodeReview, on_delete=models.CASCADE, related_name='summary')
#     summary_text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Summary for {self.code_review}"
