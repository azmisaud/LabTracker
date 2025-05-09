from django.contrib import admin
from problems.models import Problem, WeekCommit, ProblemCompletion


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
            - 'last_updated': Displays the last updated timestamp of the problem.

        search_fields (tuple): Defines the fields that can be searched using the search bar in the admin panel.
            - 'course': Allows searching by course.
            - 'semester': Allows searching by semester number.

        list_filter (tuple): Defines the fields by which the problems can be filtered.
            - 'course': Filter by course.
            - 'semester': Filter by semester.
            - 'week': Filter by week.

        ordering (tuple): Defines the default ordering of the problems in the admin panel.
            - ('course', 'semester', 'week', 'problemNumber'): Orders by course, semester, week, and problem number.

        readonly_fields (tuple): Fields that are set as read-only in the admin interface.
            - 'created_at': The timestamp when the problem was created.
            - 'updated_at': The timestamp when the problem was last updated.
    """

    list_display = ('course', 'semester', 'week', 'problemNumber', 'description', 'image')
    search_fields = ('course', 'semester', 'week', 'problemNumber')
    list_filter = ('course', 'semester', 'week')
    ordering = ('course', 'semester', 'week', 'problemNumber')

    # Optionally, you can add custom form behaviors
    fieldsets = (
        (None, {
            'fields': ('course', 'semester', 'week', 'problemNumber', 'description', 'image')
        }),
    )

@admin.register(ProblemCompletion)
class ProblemCompletionAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the ProblemCompletion model.

    This class customizes the Django Admin panel for managing `ProblemCompletion` entries,
    providing a user-friendly way to view and search student problem completion records.

    Features:
    - `list_display`: Specifies the fields displayed in the list view within the Admin panel.
      These include the student, the problem, the completion status, the solution URL, and the output image URL.
    - `search_fields`: Enables search functionality in the Admin panel for easier lookup of records.
      Searchable fields include `student` and `problem`.

    Attributes:
        list_display (tuple): Fields displayed in the admin list view.
        search_fields (tuple): Fields that can be searched in the admin interface.

    Example:
        When viewing `ProblemCompletion` entries in the Admin panel, the user will see a table listing:
        - `student`: The student who worked on the problem.
        - `problem`: The specific problem being tracked.
        - `is_completed`: Whether the problem has been completed.
        - `solution_url`: A URL to the student's solution, if provided.
        - `output_image_url`: A URL to the output image, if provided.

    This configuration helps administrators manage and track the progress of student problem completions more effectively.
    """

    # Fields to be displayed in the list view of the admin interface
    list_display = ('student', 'problem', 'is_completed', 'solution_url', 'output_image_url','ai_analysis','instructor_comment')

    # Fields that can be searched in the admin interface
    search_fields = ('student', 'problem')

@admin.register(WeekCommit)
class WeekCommitAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the WeekCommit model.

    This class customizes the Django Admin panel for managing `WeekCommit` entries,
    allowing administrators to easily track students' weekly code commits.

    Features:
    - `list_display`: Specifies the fields displayed in the list view of the Admin panel.
      These include the student, the week number, the last commit time, and the last commit hash.
    - `search_fields`: Enables search functionality in the Admin panel for quickly finding records by student or week number.

    Attributes:
        list_display (tuple): Fields displayed in the admin list view.
        search_fields (tuple): Fields that can be searched in the admin interface.

    Example:
        When viewing `WeekCommit` entries in the Admin panel, the user will see:
        - `student`: The student associated with the commit.
        - `week_number`: The week for which the commit is tracked.
        - `last_commit_time`: The timestamp of the most recent commit.
        - `last_commit_hash`: The hash of the last commit (assumed to be an SHA-1 hash).

    This configuration aids administrators in monitoring students' progress and their commit history over various weeks.
    """

    # Fields to be displayed in the list view of the admin interface
    list_display = ('student', 'week_number', 'last_commit_time', 'last_commit_hash')

    # Fields that can be searched in the admin interface
    search_fields = ('student', 'week_number')

