from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Student model.

    This class customizes how the Student model is displayed and managed
    within the Django admin interface. The list display shows key fields,
    and search functionality is provided for specific fields.
    """

    # Defines which fields will be displayed in the admin list view
    list_display = ('id', 'username', 'enrollment_number', 'faculty_number',
                    'course', 'semester', 'repo_name', 'date_of_birth')

    # Adds search functionality for the specified fields in the admin interface
    search_fields = ('username', 'email', 'enrollment_number')

