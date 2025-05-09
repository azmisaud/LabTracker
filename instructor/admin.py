from django.contrib import admin
from .models import Instructor
from django.conf import settings

class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('name', 'username')
    ordering = ('date_joined',)
    list_filter = ('is_active', 'is_staff')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields.pop('password', None)
        return form

    def save_model(self, request, obj, form, change):
        if not change:  # Only when creating a new faculty member
            first_name = obj.name.split()[1]  # Get the first name
            username=f"{first_name}amuCS"
            count = 1

            while Instructor.objects.filter(username=username).exists():
                username = f"{first_name}amuCS{count}"
                count += 1

            expected_password = f"{first_name}@{settings.TEACHER_PASSWORD_BASE}"
            obj.username = username
            obj.set_password(expected_password)  # Set the initial password
        super().save_model(request,obj,form,change)

admin.site.register(Instructor, InstructorAdmin)

from django.contrib import admin
from .models import Instructor, SelectedStudent, InstructorComment, CodeSubmission, InstructorActionLog

class SelectedStudentAdmin(admin.ModelAdmin):
    list_display = ['instructor', 'student', 'selected_at']
    list_filter = ['instructor']
    search_fields = ['student__username', 'instructor__username']
admin.site.register(SelectedStudent, SelectedStudentAdmin)

class InstructorCommentAdmin(admin.ModelAdmin):
    list_display = ['student', 'problem', 'marked_by', 'created_at']
    list_filter = ['marked_by', 'created_at']
    search_fields = ['student__username', 'problem__problemNumber']
admin.site.register(InstructorComment, InstructorCommentAdmin)

class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'problem', 'is_valid', 'reviewed_by', 'reviewed_at']
    list_filter = ['is_valid', 'reviewed_by']
    search_fields = ['student__username', 'problem__problemNumber']
admin.site.register(CodeSubmission, CodeSubmissionAdmin)

class InstructorActionLogAdmin(admin.ModelAdmin):
    list_display = ['instructor', 'student', 'problem', 'action', 'timestamp']
    list_filter = ['action', 'instructor']
    search_fields = ['student__username', 'problem__problemNumber']
admin.site.register(InstructorActionLog, InstructorActionLogAdmin)

#
# @admin.register(Mentorship)
# class MentorshipAdmin(admin.ModelAdmin):
#     list_display = ('instructor', 'student', 'is_active', 'created_at')
#     list_filter = ('is_active', 'instructor')
#     search_fields = ('instructor__name', 'student__name')
#     ordering = ('-created_at',)
#
# @admin.register(CodeReview)
# class CodeReviewAdmin(admin.ModelAdmin):
#     list_display = ('mentorship', 'rating', 'created_at', 'updated_at')
#     list_filter = ('rating', 'created_at')
#     search_fields = ('mentorship__student__name', 'mentorship__instructor__name')
#     ordering = ('-created_at',)
#
# @admin.register(CodeSummary)
# class CodeSummaryAdmin(admin.ModelAdmin):
#     list_display = ('code_review', 'created_at')
#     search_fields = ('code_review__mentorship__student__name',)
#     ordering = ('-created_at',)
