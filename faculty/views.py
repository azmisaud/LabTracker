from datetime import timedelta
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from LabTrackerAMU.decorators import faculty_required
from problems.models import Problem, ProblemCompletion, WeekCommit
from students.models import Student
from .forms import FacultyLoginForm, ChangePasswordForm, LastDateOfWeekForm
from .models import Faculty, FacultyActivity, LastDateOfWeek
from django.contrib.auth import logout
from django.contrib import messages
from .utils import update_student_data


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
    POST /faculty_login/
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
    POST /change_password/
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
            return redirect('faculty_dashboard')  # Redirect to the dashboard
    else:
        form = ChangePasswordForm(user=faculty)  # Instantiate an empty form for GET requests

    return render(request, 'faculty/change_password.html', {'form': form})  # Render the form template


@faculty_required
def faculty_logout(request):
    """
    Handles the logout process for authenticated faculty members.

    This view logs out a faculty member by calling the Django logout method,
    which removes the user from the session. It also displays a success message
    upon successful logout and redirects the faculty member to the homepage.

    Args:
        request (HttpRequest): The HTTP request object, containing metadata
        about the current session.

    Returns:
        HttpResponseRedirect: Redirects the user to the homepage after logout.
    """
    # Call Django's built-in logout function to log the user out
    logout(request)

    # Display a success message confirming the logout
    messages.success(request, 'You have successfully logged out.')

    return redirect('faculty_login')

@require_GET
@faculty_required
def get_semesters_faculty(request):
    """
    Retrieve and return a list of unique semesters for a specific course.

    This view handles GET requests to retrieve a list of distinct semesters
    for students enrolled in a particular course. The view is restricted
    to authenticated teachers using the `teacher_required` decorator, and
    only responds to GET requests due to the `require_GET` decorator.

    Args:
        request (HttpRequest): The current HTTP GET request. The course is
        expected as a query parameter (`course`).

    Returns:
        JsonResponse: A JSON response containing a list of distinct semesters
        for the specified course. The response is sent in an array format.
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
    Retrieve and return a list of faculty numbers for students in a specific course and semester.

    This view handles GET requests to retrieve a list of faculty numbers for students enrolled in
    a particular course and semester. The view is restricted to authenticated teachers using the
    `teacher_required` decorator and only accepts GET requests due to the `require_GET` decorator.

    Args:
        request (HttpRequest): The current HTTP GET request. The course and semester are expected
        as query parameters (`course`, `semester`).

    Returns:
        JsonResponse: A JSON response containing a list of faculty numbers for students in the
        specified course and semester. The response is an array of faculty numbers.
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
    Retrieve and return a list of unique weeks for problems in a specific course and semester.

    This view handles GET requests to retrieve a list of distinct weeks for problems
    associated with a particular course and semester. The view is restricted to
    authenticated teachers using the `teacher_required` decorator and accepts only
    GET requests due to the `require_GET` decorator.

    Args:
        request (HttpRequest): The current HTTP GET request. The course and semester
        are expected as query parameters (`course`, `semester`).

    Returns:
        JsonResponse: A JSON response containing a list of distinct weeks for the
        specified course and semester. The response is an array of week numbers.
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
def week_last_date_faculty(request):
    """
    Manage the setting of the last date for a specific week by a faculty member.

    This view allows a faculty member to set the last date for a particular week in their course.
    The faculty member must be logged in to access this functionality. If the request method is
    POST, it processes the submitted form data. If the form is valid, it saves the last date
    and records this action in the FacultyActivity log.

    Decorators:
    - @faculty_required: Ensures that only authenticated faculty can access this view.

    Request Types:
    - GET: Renders the form for setting the last date.
    - POST: Processes the submitted form data to set the last date.

    Parameters:
    - request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    - HttpResponse: Renders the 'faculty/week_last_date.html' template with the form for
      GET requests or redirects to the same page with a success message for POST requests.
    """
    faculty = request.user # Fetch the faculty instance

    if request.method == 'POST':
        form = LastDateOfWeekForm(request.POST)
        if form.is_valid():
            week_date = form.save()

            FacultyActivity.objects.create(
                faculty=faculty,  # Log the action under the correct faculty member
                action='Set Last Date',
                course=week_date.course,
                semester=week_date.semester,
                week=week_date.week,
                description=week_date.last_date
            )

            messages.success(request, 'Last date set successfully')
            return redirect('last_date_of_week')
    else:
        form = LastDateOfWeekForm()

    return render(request, 'faculty/set_last_date.html', {'form': form})

@require_GET
@faculty_required
def fetch_student_details_faculty(request):
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
    Render the 'check_student_details' template for teachers to view student details.

    This view provides a simple interface for teachers to access a page where they can input or
    search for student details. The form on the page likely triggers other actions to fetch or display
    student information.

    Decorators:
    - @teacher_required: Ensures that only authenticated teachers can access this view.

    Parameters:
    - request (HttpRequest): The HTTP request object.

    Returns:
    - HttpResponse: Renders the 'check_student_details.html' template for the teacher.
    """
    return render(request, 'faculty/check_student_details.html')

@faculty_required
@csrf_exempt
@require_POST
def log_activity_faculty(request):
    """
    Log a teacher's activity related to course and semester actions.

    This view handles logging specific actions performed by a teacher, such as setting deadlines,
    or other course-related activities. The action details are posted via a form and stored in the
    TeacherActivity model.

    Decorators:
    - @teacher_required: Ensures that only authenticated teachers can access this view.
    - @csrf_exempt: Allows the view to be accessed without CSRF token validation.
    - @require_POST: Ensures that only POST requests are allowed.

    Parameters:
    - request (HttpRequest): The HTTP request object, expected to contain POST data including:
      - action (str): The action performed by the teacher (e.g., 'Set Last Date').
      - course (str): The course related to the action.
      - semester (str): The semester related to the action.
      - week (str): The specific week of the semester related to the action.

    Returns:
    - JsonResponse: A success message in JSON format upon successful logging of the activity.
      Returns an error message if the teacher is not logged in.
    """

    faculty=request.user
    action = request.POST.get('action')
    course = request.POST.get('course')
    semester = request.POST.get('semester')
    week = request.POST.get('week')

    FacultyActivity.objects.create(
        faculty=faculty,
        action=action,
        course=course,
        semester=semester,
        week=week
    )

    return JsonResponse({'success': 'Activity logged successfully'})

@faculty_required
@require_GET
def fetch_whole_class_weekly_faculty(request):

    course = request.GET.get('course')
    semester = request.GET.get('semester')
    week = request.GET.get('week')

    all_student = Student.objects.filter(course=course, semester=semester).order_by('faculty_number')

    # Fetch last date for the week
    week_last_date_2 = LastDateOfWeek.objects.filter(course=course, semester=semester, week=week).first()
    last_date = week_last_date_2.last_date if week_last_date_2 else None

    # Total problems for the week
    total_problems_in_week = Problem.objects.filter(course=course, semester=semester, week=week).count()

    report_data = []

    # Loop through each student to gather progress data
    for student in all_student:
        week_commit = WeekCommit.objects.filter(student=student, week_number=week).first()

        problems_solved = ProblemCompletion.objects.filter(student=student, problem__week=week,
                                                           is_completed=True).count()

        # Determine submission status based on the last commit time and deadline
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

        # Append student data to the report
        report_data.append({
            'enrollment_number': student.enrollment_number,
            'faculty_number': student.faculty_number,
            'full_name': f"{student.first_name} {student.last_name}",
            'last_commit_time': last_commit_time,
            'problems_solved': problems_solved,
            'total_problems': total_problems_in_week,
            'status': commit_status
        })

    return JsonResponse(report_data, safe=False)

@faculty_required
def check_whole_class_weekly_faculty(request):
    return render(request, 'faculty/check_weekly_class.html')

@faculty_required
@require_GET
def fetch_whole_class_faculty(request):

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
    return render(request, 'faculty/check_whole_class.html')

@faculty_required
@csrf_exempt
@require_POST
def trigger_update_faculty(request):

    last_update = FacultyActivity.objects.filter(action='Updated the data').order_by('-timestamp').first()

    # Check if the last update was within the past hour
    if last_update and (timezone.now() - last_update.timestamp) < timedelta(hours=1):
        return JsonResponse({
            'error': f'Button is disabled for 1 hour because {last_update.teacher} updated for {last_update.course}, Semester {last_update.semester}'
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

    # Get the teacher ID from the session
    # Get the teacher object based on the session ID
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

    faculty=request.user
    # Retrieve all activities performed by other teachers, ordered by timestamp (most recent first)
    other_teacher_activities = FacultyActivity.objects.exclude(faculty=faculty).order_by('-timestamp')

    def format_activity(activity):

        # Format the timestamp in a readable format
        timestamp = format(timezone.localtime(activity.timestamp), 'd F Y, H:i')

        # Check the action type and format accordingly with the teacher's name
        if activity.action == 'Added Problem':
            return f"{timestamp} : {activity.teacher.name} added a problem in {activity.course}, Sem {activity.semester} in Week {activity.week} <br> Problem Description : {activity.description}"
        elif activity.action == 'Edited Problem':
            return f"{timestamp} : {activity.teacher.name} edited a problem in {activity.course}, Sem {activity.semester} in Week {activity.week} <br> Problem Description : {activity.description}"
        elif activity.action == 'Viewed Class Report':
            return f"{timestamp} : {activity.teacher.name} viewed the class report of {activity.course}, Sem {activity.semester}"
        elif activity.action == 'Downloaded Class Report':
            return f"{timestamp} : {activity.teacher.name} downloaded the class report of {activity.course}, Sem {activity.semester}"
        elif activity.action == 'Started a New Semester':
            return f"{timestamp} : {activity.teacher.name} started a new Semester"
        elif activity.action == 'Updated the data':
            return f"{timestamp} : {activity.teacher.name} updated the data for {activity.course}, Sem {activity.semester}"
        elif activity.action == 'Viewed Weekly Class Report':
            return f"{timestamp} : {activity.teacher.name} viewed the weekly report of {activity.course}, Sem {activity.semester}, Week {activity.week}"
        elif activity.action == 'Downloaded Weekly Class Report':
            return f"{timestamp} : {activity.teacher.name} downloaded the weekly report of {activity.course}, Sem {activity.semester}, Week {activity.week}"
        elif activity.action == 'Set Last Date':
            return f"{timestamp} : {activity.teacher.name} have set the last date for {activity.course}, Sem {activity.semester}, Week {activity.week} as {activity.description}"
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
