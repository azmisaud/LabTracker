from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """
    Admin interface for the Teacher model.

    This class customizes the display and functionality of the Teacher model
    within the Django admin site.
    """

    # Specifies which fields are displayed in the list view of the Teacher model.
    list_display = ('name',)

    # Adds a search box in the admin list view, allowing users to search by the specified fields.
    search_fields = ('name',)

