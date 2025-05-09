from datetime import timedelta
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from LabTrackerAMU.decorators import faculty_required
from problems.models import Problem, ProblemCompletion, WeekCommit
from students.models import Student
from .forms import FacultyLoginForm, ChangePasswordForm, LastDateOfWeekForm
from .models import Faculty, FacultyActivity, LastDateOfWeek
from django.contrib.auth import logout
from django.contrib import messages
from .utils import update_student_data
from django.utils.dateformat import format

def faculty_login(request):
    """
    Handles the login process for faculty members.

    This view provides a login form for faculty members and processes their login credentials.
    If the credentials are valid, the faculty member is authenticated, logged in, and redirected
    based on whether it's their first login or not.

    Behavior:
    - If the request method is `GET`, an empty login form is displayed.
    - If the request method is `POST`, the form is bound with the submitted data.
    - The function validates the form; if valid, it retrieves the username and password.
    - It uses the custom `FacultyBackend` to authenticate the faculty member.
    - Upon successful authentication:
        - The faculty member is logged in, and their session is initiated.
        - If it is the faculty member's first login, they are redirected to the change password view.
        - Otherwise, they are redirected to the faculty dashboard.
    - If authentication fails, an error message is displayed.

    Parameters:
    - `request`: The HTTP request object containing the submitted login data.

    Returns:
    - Renders the `faculty/faculty_login.html` template with the login form.
    - On successful login, redirects to either the password change view or the faculty dashboard.

    Example usage:
    ```
    POST faculty/login/
    {
        "username": "faculty_username",
        "password": "faculty_password"
    }
    ```

    Example response:
    - On successful login:
      - Redirects to 'change_password' if first login.
      - Redirects to 'faculty_dashboard' otherwise.
    - On failed login:
      - Displays a message: "Invalid username or password."

    Notes:
    - The `FacultyLoginForm` should handle username and password validation.
    - Ensure that the `Faculty` model is set up to work with Django's authentication system.
    """

    form = FacultyLoginForm()  # Instantiate the form

    if request.method == 'POST':
        form = FacultyLoginForm(request.POST)  # Bind the form with POST data
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Use the custom FacultyBackend to authenticate
            faculty = authenticate(request, username=username, password=password)

            if faculty is not None and isinstance(faculty, Faculty):  # Check if authenticated user is a faculty
                login(request, faculty)  # Log the faculty in
                if faculty.is_first_login:
                    return redirect('change_password')  # Redirect to change password view
                else:
                    return redirect('faculty_dashboard')  # Redirect to dashboard
            else:
                # Authentication failed
                messages.error(request, 'Invalid username or password.')

    return render(request, 'faculty/faculty_login.html', {'form': form})  # Pass the form to the template


@faculty_required
def change_password(request):
    """
    Handles the password change process for faculty members.

    This view allows faculty members to change their password, specifically after their first login,
    or whenever they wish to update it. It checks the validity of the new password and saves the
    updated password if the form is valid. After a successful password change, the faculty's
    `is_first_login` attribute is set to `False` and they are redirected to the faculty dashboard.

    Behavior:
    - If the request method is `POST`, the form is bound with the submitted data and validated.
    - If the form is valid, the new password is saved, and the faculty's `is_first_login` attribute is updated.
    - A success message is displayed upon successful password change, and the faculty is redirected to the dashboard.
    - If the request method is `GET`, an empty password change form is displayed.

    Decorators:
    - `@faculty_required`: Ensures that only authenticated faculty members can access this view.

    Parameters:
    - `request`: The HTTP request object containing the POST data or the request to display the form.

    Returns:
    - Renders the `faculty/change_password.html` template with the password change form.
    - On successful password change, redirects to the `faculty_dashboard`.

    Example usage:
    ```
    POST faculty/change-password/
    {
        "old_password": "current_password",
        "new_password1": "new_password",
        "new_password2": "new_password"
    }
    ```

    Example response:
    - On successful password change:
      - Displays a success message: "Password changed successfully."
      - Redirects to the `faculty_dashboard`.
    - On invalid form submission:
      - Displays form errors and reloads the form.

    Notes:
    - The `ChangePasswordForm` handles the validation of old and new passwords.
    - This view is protected by the `faculty_required` decorator to ensure only faculty can access it.
    - The `faculty.is_first_login` attribute is updated to `False` after the first successful password change.
    """
    faculty = request.user  # Get the currently logged-in faculty member

    if request.method == 'POST':
        form = ChangePasswordForm(user=faculty, data=request.POST)  # Bind the form with POST data
        if form.is_valid():
            form.save()  # Save the new password
            faculty.is_first_login = False  # Mark that the first login is completed
            faculty.save()  # Save the changes to the faculty member
            messages.success(request, 'Password changed successfully.')  # Display success message
            return redirect('faculty_login')  # Redirect to the dashboard
    else:
        form = ChangePasswordForm(user=faculty)  # Instantiate an empty form for GET requests

    return render(request, 'faculty/change_password.html', {'form': form})  # Render the form template


@faculty_required
def faculty_logout(request):
    """
    Logs out the current faculty member and redirects them to the login page.

    This view handles the logout process for faculty members. It uses Django's built-in `logout` function
    to terminate the faculty's session and then redirects them to the faculty login page. A success message
    is displayed to confirm the successful logout.

    Behavior:
    - Logs out the current faculty by clearing their session data.
    - Displays a success message confirming the logout.
    - Redirects the faculty to the login page.

    Decorators:
    - `@faculty_required`: Ensures that only authenticated faculty members can access this view.

    Parameters:
    - `request`: The HTTP request object, which contains session information to log out the current user.

    Returns:
    - Redirects the faculty to the `faculty_login` page after logout.
    - Displays a success message: "You have successfully logged out."

    Example usage:
    ```
    GET faculty/logout/
    ```

    Example response:
    - On successful logout:
      - Displays the success message: "You have successfully logged out."
      - Redirects to the faculty login page.

    Notes:
    - The `logout` function is a Django utility that handles clearing the session and performing the logout.
    - The `faculty_required` decorator ensures that only logged-in faculty members can access the logout function.
    """
    logout(request)  # Log out the current faculty member

    # Display a success message confirming the logout
    messages.success(request, 'You have successfully logged out.')

    return redirect('faculty_login')  # Redirect to the faculty login page


@require_GET
@faculty_required
def get_semesters_faculty(request):
    """
    Retrieves a list of distinct semesters associated with a specific course.

    This view is used to fetch the available semesters for a given course, which can be utilized
    by the faculty to filter students or problems based on their semester. It expects the 'course'
    parameter to be passed via the GET request, and the response is a JSON list of semesters.

    Decorators:
    - `@require_GET`: Ensures that the view can only be accessed via a GET request.
    - `@faculty_required`: Ensures that only authenticated faculty members can access this view.

    Parameters:
    - `request`: The HTTP request object, containing the GET data, including the 'course' parameter.

    Behavior:
    - Retrieves the 'course' parameter from the GET request.
    - Queries the `Student` model to find distinct semesters for students enrolled in the given course.
    - Orders the semesters numerically (ascending) and ensures there are no duplicates using `distinct()`.
    - Returns the list of semesters as a JSON response.

    Returns:
    - `JsonResponse`: A list of distinct semesters in JSON format.
      - Example: `[1, 2, 3, 4, 5]`
    - If no semesters are found, the response will be an empty list: `[]`.
    - The `safe=False` argument is used to allow non-dict objects (like a list) to be serialized.

    Example usage:
    ```
    GET faculty/get-semesters/?course=MCA
    ```

    Example response:
    ```
    [1, 2, 3, 4, 5]
    ```

    Notes:
    - The `values_list('semester', flat=True)` method extracts only the 'semester' field from the query.
    - `distinct()` ensures that only unique semesters are returned.
    - The `@faculty_required` decorator guarantees that only authenticated faculty members can call this view.
    """
    # Retrieve the 'course' parameter from the GET request.
    course = request.GET.get('course')

    # Query the database for distinct semesters associated with the given course.
    # The values_list method extracts the 'semester' field, and distinct ensures
    # there are no duplicate semesters. The results are ordered by semester.
    semester = (
        Student.objects.filter(course=course)
        .values_list('semester', flat=True)
        .distinct()
        .order_by('semester')
    )

    # Return the list of semesters as a JSON response.
    # The 'safe=False' argument allows a non-dict object to be serialized.
    return JsonResponse(list(semester), safe=False)


@require_GET
@faculty_required
def get_faculty_numbers_faculty(request):
    """
    Retrieves a list of faculty numbers for students enrolled in a specific course and semester.

    This view is used to fetch the faculty numbers of students based on the provided 'course' and
    'semester' parameters. The list of faculty numbers can be used by faculty members to identify
    or select students. The response is returned in JSON format.

    Decorators:
    - `@require_GET`: Ensures that the view can only be accessed via a GET request.
    - `@faculty_required`: Ensures that only authenticated faculty members can access this view.

    Parameters:
    - `request`: The HTTP request object, containing the GET data, including 'course' and 'semester' parameters.

    Behavior:
    - Retrieves the 'course' and 'semester' parameters from the GET request.
    - Queries the `Student` model to find all students that match the given course and semester.
    - Extracts the faculty numbers of those students and orders the list by the `faculty_number` field.
    - Returns the list of faculty numbers as a JSON response.

    Returns:
    - `JsonResponse`: A list of faculty numbers in JSON format.
      - Example: `["23CAMSA101", "23CAMSA102", "23CAMSA103"]`
    - If no faculty numbers are found, the response will be an empty list: `[]`.
    - The `safe=False` argument is used to allow non-dict objects (like a list) to be serialized.

    Example usage:
    ```
    GET faculty/get-faculty-numbers/?course=MCA&semester=3
    ```

    Example response:
    ```
    ["23CAMSA103", "23CAMSA104", "23CAMSA105"]
    ```

    Notes:
    - The `values_list('faculty_number', flat=True)` method extracts only the `faculty_number` field from the query.
    - The query is ordered by `faculty_number` to ensure the list is sorted.
    - The `@faculty_required` decorator guarantees that only authenticated faculty members can call this view.
    """
    # Retrieve the 'course' and 'semester' parameters from the GET request.
    course = request.GET.get('course')
    semester = request.GET.get('semester')

    # Query the database for students based on the course and semester, and retrieve
    # the list of faculty numbers. The list is ordered by faculty number.
    faculty_number = (
        Student.objects.filter(course=course, semester=semester)
        .values_list('faculty_number', flat=True)
        .order_by('faculty_number')
    )

    # Return the list of faculty numbers as a JSON response.
    # The 'safe=False' argument allows a non-dict object (like a list) to be serialized.
    return JsonResponse(list(faculty_number), safe=False)


@require_GET
@faculty_required
def get_weeks_faculty(request):
    """
    Retrieves a list of distinct weeks for a given course and semester.

    This view is used by faculty members to fetch the weeks associated with problems in a specific
    course and semester. The weeks are returned in ascending order and can be used for filtering or
    selecting problem sets. The response is in JSON format.

    Decorators:
    - `@require_GET`: Ensures that the view can only be accessed via a GET request.
    - `@faculty_required`: Ensures that only authenticated faculty members can access this view.

    Parameters:
    - `request`: The HTTP request object, containing the GET data, including 'course' and 'semester' parameters.

    Behavior:
    - Retrieves the 'course' and 'semester' parameters from the GET request.
    - Queries the `Problem` model to find all distinct weeks for problems that match the given course and semester.
    - Extracts the weeks from the query results and sorts them in ascending order.
    - Returns the list of distinct weeks as a JSON response.

    Returns:
    - `JsonResponse`: A list of weeks in JSON format.
      - Example: `[1, 2, 3, 4]`
    - If no weeks are found, the response will be an empty list: `[]`.
    - The `safe=False` argument is used to allow non-dict objects (like a list) to be serialized.

    Example usage:
    ```
    GET /get_weeks_faculty/?course=BSc&semester=3
    ```

    Example response:
    ```
    [1, 2, 3, 4, 5]
    ```

    Notes:
    - The `values_list('week', flat=True)` method extracts only the `week` field from the query results.
    - The query is filtered by course and semester, ensuring the results are specific to the input parameters.
    - The `@faculty_required` decorator ensures that only faculty members can access this endpoint.
    - The weeks are returned in ascending order using the `order_by('week')` method.
    """
    # Retrieve the 'course' and 'semester' parameters from the GET request.
    course = request.GET.get('course')
    semester = request.GET.get('semester')

    # Query the Problem model for distinct weeks associated with the provided course and semester.
    # The values_list method extracts the 'week' field, distinct ensures no duplicate weeks,
    # and order_by arranges the results in ascending order by week.
    week = (
        Problem.objects.filter(course=course, semester=semester)
        .values_list('week', flat=True)
        .distinct()
        .order_by('week')
    )

    # Return the list of weeks as a JSON response.
    # The 'safe=False' argument allows a non-dict object (a list) to be serialized and returned.
    return JsonResponse(list(week), safe=False)

@faculty_required
@require_http_methods(["GET", "POST"])
def week_last_date_faculty(request):
    """
    Allows faculty to set or update the last submission date for a given course, semester, and week.

    This view lets faculty define deadlines for student submissions on a per-week basis.
    If a deadline already exists for a specified course-semester-week combination, it updates the entry.
    Otherwise, it creates a new one.

    Decorators:
    - `@faculty_required`: Ensures only authenticated faculty members can access this view.
    - `@require_http_methods(["GET", "POST"])`: Restricts the view to GET and POST requests.

    Behavior:
    - GET: Renders an empty form for entering the course, semester, week, and last submission date.
    - POST:
        - Accepts form data (course, semester, week, last_date).
        - Checks if a `LastDateOfWeek` instance already exists.
        - If yes, updates it; if not, creates a new instance.
        - Logs the action using the `FacultyActivity` model for auditing.
        - Displays a success message indicating whether the date was set or updated.

    Request Data (POST):
    - `course`: The course for which to set the week deadline.
    - `semester`: The semester within the course.
    - `week`: The week number to set or update.
    - `last_date`: The deadline date to be saved.

    Returns:
    - On GET: Renders `faculty/set_last_date.html` with an empty `LastDateOfWeekForm`.
    - On valid POST: Redirects to the same page with a success message.
    - On invalid POST: Re-renders the form with error messages.

    Template:
    - `faculty/set_last_date.html`

    Example usage:
    ```http
    GET /faculty/set_last_date/
    POST /faculty/set_last_date/ with form data
    ```

    Notes:
    - Each faculty action is recorded in the `FacultyActivity` model.
    - Only one entry per course-semester-week is allowed.
    - Errors in form validation are printed to the console for debugging during development.
    """
    faculty = request.user  # The currently logged-in faculty member

    if request.method == 'POST':
        # Extract form inputs from the POST data
        course = request.POST.get('course')
        semester = request.POST.get('semester')
        week = request.POST.get('week')

        # Try to fetch existing entry for course-semester-week, if any
        instance = LastDateOfWeek.objects.filter(
            course=course, semester=semester, week=week
        ).first()

        # Bind submitted data to the form and attach instance if it exists
        form = LastDateOfWeekForm(request.POST, instance=instance)

        if form.is_valid():
            # Save form data (update or create the deadline entry)
            week_date = form.save()

            # Log the action in the FacultyActivity table
            FacultyActivity.objects.create(
                faculty=faculty,
                action='Set Last Date',
                course=week_date.course,
                semester=week_date.semester,
                week=week_date.week,
                description=str(week_date.last_date)
            )

            # Show appropriate success message
            if instance:
                messages.success(request, f"Last date updated to {week_date.last_date}")
            else:
                messages.success(request, f"Last date set to {week_date.last_date}")

            # Redirect to the same page to prevent form resubmission on reload
            return redirect(request.path)
        else:
            # Print form errors in development/debug mode
            print(form.errors)

    else:
        # Initialize a blank form for GET request
        form = LastDateOfWeekForm()

    # Render the form template
    return render(request, 'faculty/set_last_date.html', {'form': form})


@require_GET
@faculty_required
def fetch_student_details_faculty(request):
    """
    Fetches detailed information about a student based on their faculty number.

    This view allows faculty to retrieve a student's progress in terms of problems solved,
    commit history, and submission status for each week in the student's course and semester.

    Decorators:
    - `@faculty_required`: Ensures that only authenticated faculty members can access this view.
    - `@require_GET`: Restricts this view to GET requests only.

    Parameters:
    - `request`: The HTTP request object, which must include the 'faculty_number' parameter in the GET query.

    Behavior:
    - The view retrieves the student associated with the given faculty number.
    - If the student exists, the view gathers information such as:
      - Total problems solved by the student across all weeks.
      - List of weeks for the student's course and semester.
      - Problems solved by the student on a weekly basis.
      - Last commit details for each week.
      - Whether the student's submission was on time or late.
    - If the student does not exist, the view returns a 404 error with an appropriate message.

    Returns:
    - A JSON response containing the following information about the student:
      - `name`: Full name of the student.
      - `enrollment_number`: The student's enrollment number.
      - `faculty_number`: The student's faculty number.
      - `course`: The course the student is enrolled in.
      - `semester`: The semester the student is in.
      - `available_weeks`: A list of distinct weeks for the student's course and semester.
      - `problem_solved_overall`: The total number of problems solved by the student across all weeks.
      - `problems_solved_weekly`: A list of the number of problems solved by the student for each week.
      - `last_commit_times`: A list of dictionaries containing the last commit time and hash for each week,
        or "Not Committed" if no commit exists.
      - `total_problems`: A list of the total number of problems available for each week.
      - `statuses`: A list indicating whether the student's submission was "On Time", "Late", or not submitted.

    Example usage:
    ```
    GET /fetch_student_details_faculty/?faculty_number=12345
    ```

    Example response:
    ```json
    {
        "name": "John Doe",
        "enrollment_number": "EN123456",
        "faculty_number": "12345",
        "course": "BSc",
        "semester": 3,
        "available_weeks": [1, 2, 3, 4],
        "problem_solved_overall": 10,
        "problems_solved_weekly": [3, 2, 3, 2],
        "last_commit_times": [
            {"last_commit_time": "2024-10-01T12:00:00Z", "last_commit_hash": "abcd1234"},
            "Not Committed",
            {"last_commit_time": "2024-10-07T09:30:00Z", "last_commit_hash": "efgh5678"},
            "Not Committed"
        ],
        "total_problems": [4, 3, 5, 4],
        "statuses": ["On Time", "-----", "Late", "-----"]
    }
    ```

    Notes:
    - The `ProblemCompletion` model tracks problems solved by the student, and the `WeekCommit` model tracks the
      commit history for each week.
    - The `LastDateOfWeek` model is used to determine whether a submission was made on time or late, based on the last date for each week.
    - If no commit or last date exists for a particular week, the status is set to "-----".
    """
    faculty_number = request.GET.get('faculty_number')
    try:
        student = Student.objects.get(faculty_number=faculty_number)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

    # Fetch total problems solved by the student across all weeks
    problem_solved_overall = ProblemCompletion.objects.filter(student=student, is_completed=True).count()

    # Get all distinct weeks available for the student's course and semester
    available_weeks = list(Problem.objects.filter(course=student.course, semester=student.semester)
                           .values_list('week', flat=True).distinct())
    available_weeks.sort()

    # Initialize variables to hold weekly data
    problems_solved_weekly = []
    total_problems = []
    last_commit_times = []
    statuses = []

    # Iterate over each available week to gather data
    for week_number in available_weeks:
        # Get total problems for the week
        total_problems_count = Problem.objects.filter(course=student.course, semester=student.semester, week=week_number).count()
        total_problems.append(total_problems_count)

        # Count problems solved by the student in the week
        week_solved = ProblemCompletion.objects.filter(student=student, problem__week=week_number, is_completed=True).count()
        problems_solved_weekly.append(week_solved)

        # Get the last commit for the week (if exists)
        week_commit = WeekCommit.objects.filter(student=student, week_number=week_number).first()
        if week_commit:
            last_commit_times.append({
                'last_commit_time': week_commit.last_commit_time,
                'last_commit_hash': week_commit.last_commit_hash
            })
        else:
            last_commit_times.append("Not Committed")

        # Determine whether the commit was on time or late
        week_last = LastDateOfWeek.objects.filter(course=student.course, semester=student.semester, week=week_number).first()
        if week_commit and week_last:
            if week_commit.last_commit_time.date() > week_last.last_date:
                statuses.append("Late")
            else:
                statuses.append("On Time")
        else:
            statuses.append("-----")

    # Prepare the student details to be returned in the response
    student_details = {
        'name': f"{student.first_name} {student.last_name}",
        'enrollment_number': student.enrollment_number,
        'faculty_number': student.faculty_number,
        'course': student.course,
        'semester': student.semester,
        'available_weeks': available_weeks,
        'problem_solved_overall': problem_solved_overall,
        'problems_solved_weekly': problems_solved_weekly,
        'last_commit_times': last_commit_times,
        'total_problems': total_problems,
        'statuses': statuses
    }

    return JsonResponse(student_details)

@faculty_required
def check_student_details_faculty(request):
    """
    Render the 'check_student_details' template for faculty members to view student details.

    This view serves as a simple interface where faculty can search for student information by entering
    relevant details such as a student's faculty number or other identifying information.
    The form on the rendered page allows faculty to search or retrieve detailed student information,
    potentially triggering other actions or views (such as fetch_student_details_faculty) based on user input.

    Decorators:
    - @faculty_required: Ensures that only authenticated faculty members can access this view.

    Parameters:
    - request (HttpRequest): The HTTP request object.

    Returns:
    - HttpResponse: Renders the 'faculty/check_student_details.html' template for the faculty.
    """
    return render(request, 'faculty/check_student_details.html')


@faculty_required
@csrf_exempt
@require_POST
def log_activity_faculty(request):
    """
    Logs an activity performed by a faculty member, such as setting deadlines or monitoring weekly progress.

    This view allows faculty to log specific actions related to a course, semester, and week. The action is recorded
    in the `FacultyActivity` model for tracking purposes.

    Decorators:
    - `@faculty_required`: Ensures that only authenticated faculty members can access this view.
    - `@csrf_exempt`: Disables CSRF protection for this view (should be used with caution).
    - `@require_POST`: Restricts this view to POST requests only.

    Parameters:
    - `request`: The HTTP request object containing the POST data.

    POST Data:
    - `action`: A string representing the action taken by the faculty (e.g., "Set Last Date").
    - `course`: The course for which the action is being performed.
    - `semester`: The semester to which the action applies.
    - `week`: The specific week for which the action is logged.

    Behavior:
    - The view creates a new `FacultyActivity` record, logging the provided action, course, semester, and week.
    - The faculty performing the action is identified via `request.user`.

    Returns:
    - A JSON response indicating success if the activity is logged.

    Example usage:
    ```
    POST /log_activity_faculty/
    {
        "action": "Set Last Date",
        "course": "BSc Computer Science",
        "semester": 3,
        "week": 2
    }
    ```

    Example response:
    ```json
    {
        "success": "Activity logged successfully"
    }
    ```

    Notes:
    - The `FacultyActivity` model is used to log the activity, storing the faculty member's action, course, semester, and week.
    - CSRF protection is disabled in this view, so be mindful of security concerns in production.
    """
    faculty = request.user  # Get the authenticated faculty member from the request
    action = request.POST.get('action')  # Get the action from the POST request
    course = request.POST.get('course')  # Get the course from the POST request
    semester = request.POST.get('semester')  # Get the semester from the POST request
    week = request.POST.get('week')  # Get the week from the POST request

    # Log the faculty activity in the FacultyActivity model
    FacultyActivity.objects.create(
        faculty=faculty,
        action=action,
        course=course,
        semester=semester,
        week=week
    )

    # Return a success message as a JSON response
    return JsonResponse({'success': 'Activity logged successfully'})

@faculty_required
@require_GET
def fetch_whole_class_weekly_faculty(request):
    """
    Fetches the weekly progress of all students in a particular course and semester.

    This view allows faculty to retrieve details about each student's performance for a specific week,
    including the number of problems solved, the last commit time, and the submission status (on time or late).

    Decorators:
    - `@faculty_required`: Ensures that only authenticated faculty members can access this view.
    - `@require_GET`: Restricts this view to GET requests only.

    Parameters:
    - `request`: The HTTP request object, which must include the following query parameters:
      - `course`: The course for which the data is being retrieved.
      - `semester`: The semester for which the data is being retrieved.
      - `week`: The week number for which progress is being checked.

    Behavior:
    - The view retrieves all students for the given course and semester.
    - For each student, the view gathers:
      - The total number of problems solved for the week.
      - The last commit time for the week.
      - Whether the submission was made on time, late, or no commit was made.
    - If no last date for the week exists, the status is marked as "-----".

    Returns:
    - A JSON response containing a list of dictionaries for each student, with the following keys:
      - `enrollment_number`: The student's enrollment number.
      - `faculty_number`: The student's faculty number.
      - `full_name`: The student's full name.
      - `last_commit_time`: The last commit time for the week, or "No Commits" if no commit exists.
      - `problems_solved`: The number of problems the student solved for the week.
      - `total_problems`: The total number of problems available for the week.
      - `status`: The submission status, which can be "On Time", "Late", or "----".

    Example usage:
    ```
    GET /fetch_whole_class_weekly_faculty/?course=BSc&semester=3&week=2
    ```

    Example response:
    ```json
    [
        {
            "enrollment_number": "EN123456",
            "faculty_number": "12345",
            "full_name": "John Doe",
            "last_commit_time": "2024-10-07T09:30:00Z",
            "problems_solved": 3,
            "total_problems": 5,
            "status": "On Time"
        },
        {
            "enrollment_number": "EN123457",
            "faculty_number": "12346",
            "full_name": "Jane Smith",
            "last_commit_time": "No Commits",
            "problems_solved": 0,
            "total_problems": 5,
            "status": "----"
        }
    ]
    ```

    Notes:
    - The `LastDateOfWeek` model is used to determine the last allowed submission date for the week.
    - The `ProblemCompletion` model tracks the problems solved by the student.
    - The `WeekCommit` model tracks the last commit time for each student and week.
    - If no commit or last date exists for a particular week, the status is marked as "-----".
    """
    course = request.GET.get('course')  # Get the course from the query parameters
    semester = request.GET.get('semester')  # Get the semester from the query parameters
    week = request.GET.get('week')  # Get the week number from the query parameters

    # Fetch all students for the course and semester, ordered by faculty number
    all_student = Student.objects.filter(course=course, semester=semester).order_by('faculty_number')

    # Fetch the last date for the week, if it exists
    week_last_date_2 = LastDateOfWeek.objects.filter(course=course, semester=semester, week=week).first()
    last_date = week_last_date_2.last_date if week_last_date_2 else None

    # Get the total number of problems for the week
    total_problems_in_week = Problem.objects.filter(course=course, semester=semester, week=week).count()

    report_data = []  # Initialize a list to hold the report data for each student

    # Loop through each student to gather their weekly progress
    for student in all_student:
        # Fetch the last commit for the student in the given week
        week_commit = WeekCommit.objects.filter(student=student, week_number=week).first()

        # Count the problems solved by the student for the week
        problems_solved = ProblemCompletion.objects.filter(student=student, problem__week=week, is_completed=True).count()

        # Determine the submission status based on the last commit time and deadline
        if last_date:
            if week_commit:
                last_commit_time = week_commit.last_commit_time
                if last_commit_time.date() > last_date:
                    commit_status = "Late"
                else:
                    commit_status = "On Time"
            else:
                last_commit_time = "No Commits"
                commit_status = "----"
        else:
            if week_commit:
                last_commit_time = week_commit.last_commit_time
                commit_status = "-----"
            else:
                last_commit_time = "No Commits"
                commit_status = "-----"

        # Append the student's progress data to the report
        report_data.append({
            'enrollment_number': student.enrollment_number,
            'faculty_number': student.faculty_number,
            'full_name': f"{student.first_name} {student.last_name}",
            'last_commit_time': last_commit_time,
            'problems_solved': problems_solved,
            'total_problems': total_problems_in_week,
            'status': commit_status
        })

    # Return the report data as a JSON response
    return JsonResponse(report_data, safe=False)

@faculty_required
def check_whole_class_weekly_faculty(request):
    return render(request, 'faculty/check_weekly_class.html')

@faculty_required
@require_GET
def fetch_whole_class_faculty(request):
    """
        Fetches a weekly progress report for all students in a specific course and semester.

        This view is used by faculty to retrieve a comprehensive report on every student's weekly
        performance within a selected course and semester. For each student, the view provides:
        - Problems solved
        - Last commit time
        - Submission timeliness (On Time, Late, or Not Submitted)

        Decorators:
        - `@faculty_required`: Ensures that only authenticated faculty members can access this view.
        - `@require_GET`: Restricts the view to GET requests only.

        Parameters:
        - `request`: The HTTP request object. Must include the following query parameters:
            - `course`: The course code or name (e.g., 'BCA', 'MCA').
            - `semester`: The semester number (e.g., '1', '2').

        Behavior:
        - Retrieves all students enrolled in the given course and semester.
        - For each student:
            - Iterates over each available week.
            - Gathers data on total problems assigned, problems solved, last commit time, and submission status.
            - Determines commit status based on comparison between the last commit time and the last allowed date for that week.

        Returns:
        - A JSON response containing a list of student progress dictionaries.
          Each dictionary contains:
            - `enrollment_number`: The student's enrollment number.
            - `faculty_number`: The student's faculty number.
            - `name`: Full name of the student.
            - `weeks_data`: A list of dictionaries for each week, containing:
                - `week`: Week number.
                - `total_problems`: Number of problems assigned for the week.
                - `problems_solved`: Number of problems the student completed for that week.
                - `last_commit_time`: Timestamp of the student's last GitHub commit or "No Commits".
                - `commit_status`: Status of the submission ("On Time", "Late", "-----", or "----").

        Example usage:
        ```
        GET /fetch_whole_class_faculty/?course=BCA&semester=3
        ```

        Example response:
        ```json
        [
            {
                "enrollment_number": "EN10001",
                "faculty_number": "FN10001",
                "name": "Alice Smith",
                "weeks_data": [
                    {
                        "week": 1,
                        "total_problems": 4,
                        "problems_solved": 3,
                        "last_commit_time": "2024-10-01T12:00:00Z",
                        "commit_status": "On Time"
                    },
                    {
                        "week": 2,
                        "total_problems": 3,
                        "problems_solved": 1,
                        "last_commit_time": "No Commits",
                        "commit_status": "----"
                    }
                ]
            },
            {
                "enrollment_number": "EN10002",
                "faculty_number": "FN10002",
                "name": "Bob Johnson",
                "weeks_data": [
                    ...
                ]
            }
        ]
        ```

        Notes:
        - The `Problem` model defines available problems for each course, semester, and week.
        - The `ProblemCompletion` model tracks completed problems by each student.
        - The `WeekCommit` model stores the last GitHub commit time and hash for each student-week.
        - The `LastDateOfWeek` model stores the final submission deadline per week for evaluation.

        Edge cases:
        - If no commit exists, the status is marked as "----" or "-----" depending on whether a last date exists.
        - If no problems are defined for a week, the total problem count will be 0.
        """

    course = request.GET.get('course')
    semester = request.GET.get('semester')

    all_student = Student.objects.filter(course=course, semester=semester).order_by('faculty_number')
    available_weeks = list(Problem.objects.filter(course=course, semester=semester).values_list('week', flat=True).distinct())
    available_weeks.sort()

    report_data = []

    for student in all_student:
        weeks_data = []

        for week in available_weeks:
            week_commit = WeekCommit.objects.filter(student=student, week_number=week).first()
            problems_solved = ProblemCompletion.objects.filter(student=student, problem__week=week, is_completed=True).count()
            total_problems = Problem.objects.filter(course=course, semester=semester, week=week).count()
            week_last = LastDateOfWeek.objects.filter(course=course, semester=semester, week=week).first()
            last_date = week_last.last_date if week_last else None

            if last_date:
                if week_commit:
                    last_commit_time = week_commit.last_commit_time
                    if last_commit_time.date() > last_date:
                        commit_status = "Late"
                    else:
                        commit_status = "On Time"
                else:
                    last_commit_time = "No Commits"
                    commit_status = "----"
            else:
                if week_commit:
                    last_commit_time = week_commit.last_commit_time
                    commit_status = "-----"
                else:
                    last_commit_time = "No Commits"
                    commit_status = "-----"

            weeks_data.append({
                'week': week,
                'total_problems': total_problems,
                'problems_solved': problems_solved,
                'last_commit_time': last_commit_time,
                'commit_status': commit_status
            })

        report_data.append({
            'enrollment_number': student.enrollment_number,
            'faculty_number': student.faculty_number,
            'name': f"{student.first_name} {student.last_name}",
            'weeks_data': weeks_data
        })

    return JsonResponse(report_data, safe=False)

@faculty_required
def check_whole_class_faculty(request):
    """
       Renders the interface for faculty to view the weekly performance of the entire class.

       This view provides access to a frontend page where faculty members can select a course and semester,
       and then view a detailed report of all students' weekly submissions and commit status.

       Decorators:
       - `@faculty_required`: Ensures that only authenticated faculty members can access this view.

       Parameters:
       - `request`: The HTTP request object (typically a GET request when accessing the page).

       Behavior:
       - Renders the `check_whole_class.html` template from the `faculty` directory.
       - The actual data for the report is fetched asynchronously via JavaScript (likely from
         the `fetch_whole_class_faculty` endpoint).

       Template:
       - `faculty/check_whole_class.html`

       Example usage:
       ```
       GET /faculty/check-whole-class/
       ```

       Notes:
       - This view only serves the HTML page.
       - All dynamic data (student submissions, commit status, etc.) is retrieved separately via AJAX/JS using a JSON API.
    """
    return render(request, 'faculty/check_whole_class.html')

@faculty_required
@csrf_exempt
@require_POST
def trigger_update_faculty(request):
    """
       Allows a faculty member to manually trigger an update for student data
       for a specific course and semester.

       This view prevents excessive or repeated updates by enforcing a cooldown
       of 1 hour between updates for all faculty members. Only POST requests are allowed.

       Decorators:
       - `@faculty_required`: Restricts access to authenticated faculty users only.
       - `@csrf_exempt`: Temporarily disables CSRF protection (ensure this is safe or protect it another way).
       - `@require_POST`: Ensures that only POST requests are accepted.

       Parameters:
       - `request`: The HTTP POST request object. It must include:
           - `course`: The course identifier (e.g., 'BCA').
           - `semester`: The semester number (e.g., '3').

       Behavior:
       - Checks whether any faculty has triggered a data update in the last hour.
       - If an update was made within the past hour, returns a JSON error response indicating who triggered it and for which course and semester.
       - If allowed, invokes the `update_student_data(course, semester)` function to refresh data (such as pulling latest submissions, syncing repositories, etc.).
       - Records the activity using the `FacultyActivity` model for audit and cooldown purposes.

       Returns:
       - `JsonResponse`:
           - On success: `{ "success": "Data updated successfully" }`
           - On cooldown error: `{ "error": "Button is disabled for 1 hour because ..." }`

       Example request:
       ```http
       POST /faculty/trigger-update/
       Content-Type: application/x-www-form-urlencoded

       course=BCA&semester=3
       ```

       Notes:
       - The cooldown is global across faculty. If *any* faculty triggers an update, the button is disabled for all for the next hour.
       - Consider enhancing with per-course-per-semester cooldown or scoped permissions depending on future needs.
       - The update logic itself is encapsulated in the `update_student_data()` function, which should be idempotent and safely re-runnable.
    """
    last_update = FacultyActivity.objects.filter(action='Updated the data').order_by('-timestamp').first()

    # Check if the last update was within the past hour
    if last_update and (timezone.now() - last_update.timestamp) < timedelta(hours=1):
        return JsonResponse({
            'error': f'Button is disabled for 1 hour because {last_update.faculty.name} updated for {last_update.course}, Semester {last_update.semester}'
        })

    faculty=request.user
    course = request.POST.get('course')
    semester = request.POST.get('semester')

    # Call the function to update student data based on the selected course and semester
    update_student_data(course, semester)

    # Log the teacher's activity
    FacultyActivity.objects.create(
        faculty=faculty,
        action='Updated the data',
        course=course,
        semester=semester,
    )

    return JsonResponse({'success': 'Data updated successfully'})

@faculty_required
@require_GET
def delete_old_students_faculty(request):
    """
       Allows a faculty member to initiate a new semester by deleting inactive or outdated student accounts
       that have been on the platform for more than 150 days.

       This operation is restricted to ensure it is not executed too frequently:
       it cannot be performed if a "new semester" was already started within the last 150 days.

       Decorators:
       - `@faculty_required`: Ensures the user is an authenticated faculty member.
       - `@require_GET`: Only allows HTTP GET requests to access this view.

       Process:
       1. Defines a cutoff of 150 days before the current time.
       2. Checks if a "Started a New Semester" action has been logged within the last 150 days.
          - If such an activity exists, returns an error preventing duplicate semester resets.
       3. Filters students whose accounts were created more than 150 days ago.
          - Superusers and staff accounts are excluded from deletion.
       4. Deletes those student records and logs the action as a new semester start in `FacultyActivity`.
       5. Returns a JSON response indicating either the number of students deleted or an appropriate error message.

       Parameters:
       - `request`: The HTTP GET request object.

       Returns:
       - `JsonResponse`:
           - On recent semester activity: `{ "error": "A new semester has been started recently." }`
           - If no eligible students found: `{ "error": "No students have completed 150 days on the platform." }`
           - On success: `{ "success": "<number> students deleted successfully" }`

       Notes:
       - This logic ensures safety by enforcing a minimum interval between resets.
       - Intended for cleaning up stale accounts during transitions between academic terms.
       - Consider backing up student data or adding a confirmation step for production environments.
    """
    faculty=request.user

    # Define the cutoff date (150 days from the current time)
    cutoff_date = timezone.now() - timedelta(days=150)

    # Check if a new semester has been started in the last 150 days
    recent_activity_exists = FacultyActivity.objects.filter(
        action='Started a New Semester',
        timestamp__gte=cutoff_date
    ).exists()

    if recent_activity_exists:
        # Return an error if a new semester was started recently
        return JsonResponse({'error': 'A new semester has been started recently.'})

    # Find students who have been on the platform for more than 150 days
    # Exclude superuser and staff accounts from deletion
    students_to_delete = Student.objects.filter(
        date_joined__lte=cutoff_date
    ).exclude(is_superuser=True,is_staff=True)

    if not students_to_delete.exists():
        # Return an error if no eligible students are found for deletion
        return JsonResponse({'error': 'No students have completed 150 days on the platform.'})

    # Perform the deletion and capture the number of students deleted
    num_deleted, _ = students_to_delete.delete()

    # Log the activity of starting a new semester
    FacultyActivity.objects.create(
        faculty=faculty,
        action='Started a New Semester',
    )

    # Return a success response with the number of deleted students
    return JsonResponse({'success': f'{num_deleted} students deleted successfully'})

@faculty_required
def your_activity_faculty(request):
    """
       Displays the activity log of the currently logged-in faculty member.

       This view retrieves all actions performed by the faculty member (such as editing/adding problems,
       generating reports, starting a new semester, updating data, etc.) and displays them in a paginated
       format (15 per page), ordered from the most recent to the oldest.

       Decorators:
       - `@faculty_required`: Ensures the view is only accessible to authenticated faculty members.

       Workflow:
       1. Retrieves the current faculty user from the session (`request.user`).
       2. Fetches all `FacultyActivity` records associated with that faculty member, ordered by timestamp descending.
       3. Formats each activity into a human-readable HTML string using a helper function `format_activity2()`.
          - The function converts timestamps to the local timezone and returns descriptive text depending on the action type.
          - Handles actions like "Added Problem", "Viewed Report", "Started a New Semester", etc.
       4. Paginates the formatted activity list, 15 entries per page using Django's `Paginator`.
       5. Passes the paginated activity log and faculty object into the context for rendering.

       Parameters:
       - `request`: The HTTP GET request object.

       Returns:
       - `HttpResponse`: Renders the `faculty/your_activity.html` template with paginated activity data.

       Template Context:
       - `faculty`: The current faculty user.
       - `page_obj`: The paginated page of formatted activity strings.

       Notes:
       - This log helps faculty members keep track of their administrative actions within the system.
       - Formatting includes HTML line breaks (`<br>`) to improve readability in the template.
    """
    faculty=request.user

    # Retrieve all activities of the teacher, sorted by timestamp (most recent first)
    all_activity = FacultyActivity.objects.filter(faculty=faculty).order_by('-timestamp')

    def format_activity2(activity):
        timestamp = format(timezone.localtime(activity.timestamp), 'd F Y, H:i')

        # Check the action type and format accordingly
        if activity.action == 'Added Problem':
            return f"{timestamp} : You added a problem in {activity.course}, Sem {activity.semester} in Week {activity.week} <br> Problem Description : {activity.description}"
        elif activity.action == 'Edited Problem':
            return f"{timestamp} : You edited a problem in {activity.course}, Sem {activity.semester} in Week {activity.week} <br> Problem Description : {activity.description}"
        elif activity.action == 'Viewed Class Report':
            return f"{timestamp} : You viewed the class report of {activity.course}, Sem {activity.semester}"
        elif activity.action == 'Downloaded Class Report':
            return f"{timestamp} : You downloaded the class report of {activity.course}, Sem {activity.semester}"
        elif activity.action == 'Started a New Semester':
            return f"{timestamp} : You started a new Semester"
        elif activity.action == 'Updated the data':
            return f"{timestamp} : You updated the data for {activity.course}, Sem {activity.semester}"
        elif activity.action == 'Viewed Weekly Class Report':
            return f"{timestamp} : You viewed the weekly report of {activity.course}, Sem {activity.semester}, Week {activity.week}"
        elif activity.action == 'Downloaded Weekly Class Report':
            return f"{timestamp} : You downloaded the weekly report of {activity.course}, Sem {activity.semester}, Week {activity.week}"
        elif activity.action == 'Set Last Date':
            return f"{timestamp} : You have set the last date for {activity.course}, Sem {activity.semester}, Week {activity.week} as {activity.description}"
        else:
            return "Unknown activity"

    # Format each activity into a readable string
    format_activity = [format_activity2(activity) for activity in all_activity]

    # Paginate the activity list, with 15 activities per page
    paginator = Paginator(format_activity, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prepare the context for the template
    context = {
        'faculty': faculty,
        'page_obj': page_obj
    }

    # Render the activity page
    return render(request, 'faculty/your_activity.html', context)

@faculty_required
def other_activity_faculty(request):
    """
        Displays the activity log of all other faculty members except the one currently logged in.

        This view is intended to give faculty members insight into the administrative actions performed
        by their peers (e.g., adding/editing problems, downloading reports, updating data, etc.).

        Decorators:
        - `@faculty_required`: Ensures the view is only accessible to authenticated faculty users.

        Workflow:
        1. Retrieves the currently logged-in faculty user from the request.
        2. Queries the `FacultyActivity` model for all activity logs **not** performed by the current faculty.
           Activities are ordered in reverse chronological order (most recent first).
        3. Each activity is formatted into a readable string via the `format_activity()` helper function.
           This function includes the timestamp, action, course/semester/week, and a description,
           and attributes the activity to the correct faculty name.
        4. Paginate the list of formatted activities with 15 entries per page using Django’s `Paginator`.
        5. Renders the results using the `faculty/other_activity.html` template.

        Parameters:
        - `request`: The HTTP GET request object.

        Returns:
        - `HttpResponse`: Renders a template with a paginated list of faculty activities not performed
          by the current user.

        Template Context:
        - `page_obj`: A paginated list of formatted activity descriptions from other faculty.

        Notes:
        - Useful for maintaining transparency and collaboration across teaching staff.
        - Activities include HTML formatting such as `<br>` for better display in templates.
    """
    faculty=request.user
    # Retrieve all activities performed by other teachers, ordered by timestamp (most recent first)
    other_teacher_activities = FacultyActivity.objects.exclude(faculty=faculty).order_by('-timestamp')

    def format_activity(activity):

        # Format the timestamp in a readable format
        timestamp = format(timezone.localtime(activity.timestamp), 'd F Y, H:i')

        # Check the action type and format accordingly with the teacher's name
        if activity.action == 'Added Problem':
            return f"{timestamp} : {activity.faculty.name} added a problem in {activity.course}, Sem {activity.semester} in Week {activity.week} <br> Problem Description : {activity.description}"
        elif activity.action == 'Edited Problem':
            return f"{timestamp} : {activity.faculty.name} edited a problem in {activity.course}, Sem {activity.semester} in Week {activity.week} <br> Problem Description : {activity.description}"
        elif activity.action == 'Viewed Class Report':
            return f"{timestamp} : {activity.faculty.name} viewed the class report of {activity.course}, Sem {activity.semester}"
        elif activity.action == 'Downloaded Class Report':
            return f"{timestamp} : {activity.faculty.name} downloaded the class report of {activity.course}, Sem {activity.semester}"
        elif activity.action == 'Started a New Semester':
            return f"{timestamp} : {activity.faculty.name} started a new Semester"
        elif activity.action == 'Updated the data':
            return f"{timestamp} : {activity.faculty.name} updated the data for {activity.course}, Sem {activity.semester}"
        elif activity.action == 'Viewed Weekly Class Report':
            return f"{timestamp} : {activity.faculty.name} viewed the weekly report of {activity.course}, Sem {activity.semester}, Week {activity.week}"
        elif activity.action == 'Downloaded Weekly Class Report':
            return f"{timestamp} : {activity.faculty.name} downloaded the weekly report of {activity.course}, Sem {activity.semester}, Week {activity.week}"
        elif activity.action == 'Set Last Date':
            return f"{timestamp} : {activity.faculty.name} have set the last date for {activity.course}, Sem {activity.semester}, Week {activity.week} as {activity.description}"
        else:
            return "Unknown activity"

    # Format the activities into readable strings
    formatted_other_teacher_activities = [format_activity(activity) for activity in other_teacher_activities]

    # Paginate the activity list, with 15 activities per page
    paginator = Paginator(formatted_other_teacher_activities, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prepare the context for the template
    context = {
        'page_obj': page_obj
    }

    # Render the activity page for other teachers' activities
    return render(request, 'faculty/other_activity.html', context)

@faculty_required
def fetch_graph_data_faculty(request):
    """
        Provides categorized graph data about student problem completion for a specific week across all
        course-semester combinations. Used in visual analytics for faculty members.

        Decorators:
        - `@faculty_required`: Ensures only authenticated faculty users can access this view.

        Query Parameters:
        - `week` (GET): The week number to fetch data for. Defaults to 1 if not provided.

        Workflow:
        1. Retrieves all distinct course-semester pairs where students are not superusers or staff.
        2. Iterates through each course-semester pair to:
           - Check if problems exist for the selected week.
           - Count how students are categorized into five groups:
             a. `late_solved`: Solved all problems but after the deadline.
             b. `late_unsolved`: Submitted late and did not solve all problems.
             c. `on_time_solved`: Solved all problems on time.
             d. `on_time_unsolved`: Submitted on time but didn't solve all.
             e. `not_committed`: Didn't submit any code at all.
        3. Uses `WeekCommit` and `LastDateOfWeek` models to determine submission timeliness.
        4. Returns the compiled statistics as a JSON array for chart rendering.

        Returns:
        - `JsonResponse`: A list of dictionaries, each containing:
            - `course`: Course name
            - `semester`: Semester number
            - `late_solved`: Count of students who submitted late but solved all problems
            - `late_unsolved`: Submitted late and didn’t solve all
            - `on_time_solved`: Submitted on time and solved all
            - `on_time_unsolved`: Submitted on time but didn’t solve all
            - `not_committed`: Didn’t submit any code

        Example Response:
        ```json
        [
            {
                "course": "B.C.A",
                "semester": 2,
                "late_solved": 4,
                "late_unsolved": 3,
                "on_time_solved": 10,
                "on_time_unsolved": 5,
                "not_committed": 2
            },
            ...
        ]
        ```

        This endpoint supports faculty dashboards for tracking student submission performance visually.
    """
    selected_week = int(request.GET.get('week', 1))

    # Get distinct course-semester combinations of non-superuser, non-staff students
    course_semester_combinations = Student.objects.filter(is_superuser=False, is_staff=False).values('course',
                                                                                                     'semester').distinct()

    # Initialize an empty list to hold the graph data
    graph_data = []

    # Loop over each course-semester combination to collect data
    for combination in course_semester_combinations:
        course = combination['course']
        semester = combination['semester']

        # Check if problems exist for the selected week for this course and semester
        if not Problem.objects.filter(course=course, semester=semester, week=selected_week).exists():
            continue  # Skip this combination if no problems are found

        # Retrieve all students for the current course and semester
        students = Student.objects.filter(course=course, semester=semester)

        # Count the total number of problems for the current course, semester, and week
        total_problems = Problem.objects.filter(course=course, semester=semester, week=selected_week).count()

        # Initialize counters for different categories
        late_solved = 0
        late_unsolved = 0
        on_time_solved = 0
        on_time_unsolved = 0
        not_committed = 0

        # Iterate through each student to classify their activity
        for student in students:
            # Count the number of solved problems for the student in the selected week
            solved_problems = ProblemCompletion.objects.filter(
                student=student,
                problem__course=course,
                problem__semester=semester,
                problem__week=selected_week,
                is_completed=True
            ).count()

            # Retrieve the student's last commit for the selected week
            last_commit = WeekCommit.objects.filter(student=student, week_number=selected_week).first()

            # Retrieve the last date allowed for the selected week
            week_last = LastDateOfWeek.objects.filter(course=course, semester=semester, week=selected_week).first()

            if last_commit:
                if week_last:
                    # Compare the commit date with the last allowed date
                    if last_commit.last_commit_time.date() > week_last.last_date:
                        # Classify the student based on whether they solved all problems or not
                        if solved_problems == total_problems:
                            late_solved += 1
                        else:
                            late_unsolved += 1
                    else:
                        if solved_problems == total_problems:
                            on_time_solved += 1
                        else:
                            on_time_unsolved += 1
                else:
                    # If no last date is available, assume it's on time
                    if solved_problems == total_problems:
                        on_time_solved += 1
                    else:
                        on_time_unsolved += 1
            else:
                # If no commit is made, classify the student as not committed
                not_committed += 1

        # Append the collected data for this course-semester combination to the graph data list
        graph_data.append({
            'course': course,
            'semester': semester,
            'late_solved': late_solved,
            'late_unsolved': late_unsolved,
            'on_time_solved': on_time_solved,
            'on_time_unsolved': on_time_unsolved,
            'not_committed': not_committed
        })

    # Return the graph data as a JSON response
    return JsonResponse(graph_data, safe=False)

@faculty_required
def faculty_dashboard(request):
    """
       Displays the faculty dashboard, showing the latest activities of the logged-in faculty
       and other teachers. The dashboard includes formatted activity details for both the logged-in
       teacher and other teachers.

       Decorators:
       - `@faculty_required`: Ensures that only authenticated faculty users can access this view.

       Workflow:
       1. Retrieves the latest 4 activities of the logged-in teacher (your activities).
       2. Retrieves the latest 4 activities of other teachers (other teacher activities).
       3. Formats the activity data for both the logged-in teacher and other teachers into readable strings.
       4. Passes the formatted activity data to the template for display.

       Template Context:
       - `faculty`: The logged-in faculty user.
       - `your_activities`: A list of formatted activities of the logged-in faculty.
       - `other_teacher_activities`: A list of formatted activities of other teachers.

       Returns:
       - `HttpResponse`: Renders the `faculty_dashboard.html` template with the context.

       Helper function `format_activity`:
       - Formats activity details based on the action type (e.g., "Added Problem", "Edited Problem").
       - Takes into account whether the activity is performed by the logged-in faculty or other teachers.

       Example of formatted activity messages:
       - "You added a problem in B.C.A, Sem 2 in Week 4 <br> Problem Description: Problem description here"
       - "Dr. Smith edited a problem in M.C.A, Sem 1 in Week 3 <br> Problem Description: Another description"

       This view is intended for the faculty dashboard to display a concise list of recent activities for the faculty member.
    """
    faculty=request.user

    # Fetch the latest 4 activities of the logged-in teacher and other teachers
    your_activities = FacultyActivity.objects.filter(faculty=faculty).order_by('-timestamp')[:4]
    other_teacher_activities = FacultyActivity.objects.exclude(faculty=faculty).order_by('-timestamp')[:4]

    # Helper function to format activities for display
    def format_activity(activity, is_your_activity=False):
        timestamp = format(timezone.localtime(activity.timestamp), 'd F Y, H:i')
        teacher_name = "You" if is_your_activity else activity.faculty.name

        action_messages = {
            'Added Problem': f"{teacher_name} added a problem in {activity.course}, Sem {activity.semester} in Week {activity.week} <br> Problem Description: {activity.description}",
            'Edited Problem': f"{teacher_name} edited a problem in {activity.course}, Sem {activity.semester} in Week {activity.week} <br> Problem Description: {activity.description}",
            'Viewed Class Report': f"{teacher_name} viewed the class report of {activity.course}, Sem {activity.semester}",
            'Downloaded Class Report': f"{teacher_name} downloaded the class report of {activity.course}, Sem {activity.semester}",
            'Started a New Semester': f"{teacher_name} started a new Semester",
            'Updated the data': f"{teacher_name} updated the data for {activity.course}, Sem {activity.semester}",
            'Viewed Weekly Class Report': f"{teacher_name} viewed the weekly report of {activity.course}, Sem {activity.semester}, Week {activity.week}",
            'Downloaded Weekly Class Report': f"{teacher_name} downloaded the weekly report of {activity.course}, Sem {activity.semester}, Week {activity.week}",
            'Set Last Date': f"{teacher_name} set the last date for {activity.course}, Sem {activity.semester}, Week {activity.week} as {activity.description}"
        }

        return action_messages.get(activity.action, "Unknown activity")

    # Format activities for display
    formatted_your_activities = [format_activity(activity, is_your_activity=True) for activity in your_activities]
    formatted_other_teacher_activities = [format_activity(activity) for activity in other_teacher_activities]

    context = {
        'faculty':faculty,
        'your_activities': formatted_your_activities,
        'other_teacher_activities': formatted_other_teacher_activities
    }

    return render(request, 'faculty/faculty_dashboard.html', context)
