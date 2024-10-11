
from django.contrib import admin
from .models import Faculty, FacultyActivity, LastDateOfWeek
from django.conf import settings

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('name', 'username')
    ordering = ('date_joined',)
    list_filter = ('is_active', 'is_staff')

    # Custom form to hide the password field
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Remove password field from the form
        form.base_fields.pop('password', None)
        return form

    def save_model(self, request, obj, form, change):
        if not change:  # Only when creating a new faculty member
            first_name = obj.name.split()[1]  # Get the first name
            username=f"{first_name}amuCS"

            count = 1

            while Faculty.objects.filter(username=username).exists():
                username = f"{username}amuCS{count}"
                count += 1

            expected_password = f"{first_name}@{settings.TEACHER_PASSWORD_BASE}"
            obj.username = username
            obj.set_password(expected_password)  # Set the initial password
        super().save_model(request,obj,form,change)

# Register the Faculty model with the admin site
admin.site.register(Faculty, FacultyAdmin)

class FacultyActivityAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'action', 'timestamp', 'course', 'semester')  # Fields to display in the list view
    list_filter = ('faculty', 'course', 'semester', 'timestamp')  # Fields to filter the list view
    search_fields = ('faculty__username', 'action', 'course')  # Searchable fields
    ordering = ('-timestamp',)  # Default ordering by timestamp descending

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

# Register the FacultyActivity model with the admin interface
admin.site.register(FacultyActivity, FacultyActivityAdmin)

class LastDateOfWeekAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'week', 'last_date')  # Fields to display in the list view
    list_filter = ('course', 'semester', 'week')  # Fields to filter the list view
    search_fields = ('course',)  # Searchable fields
    ordering = ('course', 'semester', 'week')  # Default ordering

admin.site.register(LastDateOfWeek, LastDateOfWeekAdmin)  # Register LastDateOfWeek model
