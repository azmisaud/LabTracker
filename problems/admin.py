from django.contrib import admin
from problems.models import Problem


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    """
    A Django admin interface configuration for the Problem model.

    This class customizes how the Problem model is displayed and managed in the Django admin panel.

    Attributes:
        list_display (tuple): Defines the fields to be displayed in the admin list view for Problem objects.
            - 'course': Displays the course the problem is associated with.
            - 'semester': Displays the semester number.
            - 'week': Displays the week number.
            - 'problemNumber': Displays the unique problem number.
            - 'description': Displays a brief description of the problem.
            - 'image': Displays a reference to the image related to the problem (if any).

        search_fields (tuple): Defines the fields that can be searched using the search bar in the admin panel.
            - 'course': Allows searching by course.
            - 'semester': Allows searching by semester number.

    Decorators:
        @admin.register(Problem): Registers the Problem model with this custom configuration in the Django admin site.

    Example:
        In the Django admin interface, when managing problems, the list view will display columns for the course, semester,
        week, problem number, description, and an image field (if available). Users can search through problems by course
        or semester.
    """

    list_display = ('course', 'semester', 'week', 'problemNumber', 'description', 'image')
    search_fields = ('course', 'semester')

