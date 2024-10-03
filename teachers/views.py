from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import TeacherLoginForm, WeekLastDateForm
from .models import Teacher, TeacherActivity, WeekLastDate
from LabTrackerAMU.decorators import teacher_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from students.models import Student
from problems.models import Problem, ProblemCompletion, WeekCommit
from .utils import update_student_data
from datetime import timedelta
from django.utils import timezone
from django.core.paginator import Paginator

def teacher_login(request):
    """
    Handles the login process for teachers.

    This view processes both GET and POST requests to handle teacher login.
    It validates the teacher's selection and password, authenticating them if
    the credentials are correct. Upon successful login, the teacher is redirected
    to the dashboard. If the login fails, an error message is displayed.

    Args:
        request (HttpRequest): The HTTP request object, containing metadata
        about the request.

    Returns:
        HttpResponse: Renders the login page with a form for GET requests.
        Redirect: Redirects the teacher to the dashboard upon successful login.
    """

    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['teacher']
            password = form.cleaned_data['password']

            # Extract the teacher's first name and generate the expected password.
            first_name = teacher.name.split()[1]
            expected_password = f"{first_name}@{settings.TEACHER_PASSWORD_BASE}"

            # Authenticate the teacher based on the provided password.
            if password == expected_password:
                # Store teacher's ID in session upon successful login.
                request.session['teacher_id'] = teacher.id
                return redirect('teacher_login')
            else:
                # Display an error message if the password is incorrect.
                messages.error(request, 'Incorrect password.')
    else:
        # If the request is GET, initialize an empty login form.
        form = TeacherLoginForm()

    # Render the login page with the form.
    return render(request, 'teachers/login.html', {'form': form})


@teacher_required
def teacher_logout(request):
    """
    Handles the logout process for authenticated teachers.

    This view logs out a teacher by removing their `teacher_id` from the session.
    It also displays a success message upon successful logout and redirects the
    teacher to the homepage. The view is protected by the `teacher_required`
    decorator, ensuring only authenticated teachers can access it.

    Args:
        request (HttpRequest): The HTTP request object, containing metadata
        about the current session.

    Returns:
        HttpResponseRedirect: Redirects the user to the homepage after logout.
    """

    # Check if the session contains 'teacher_id'.
    if 'teacher_id' in request.session:
        # Remove 'teacher_id' from the session, effectively logging out the teacher.
        del request.session['teacher_id']
        # Display a success message confirming the logout.
        messages.success(request, 'You have successfully logged out.')

    # Redirect to the homepage after logout.
    return redirect('homepage')


@require_GET
@teacher_required
def get_semesters2(request):
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
@teacher_required
def get_faculty_numbers(request):
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
@teacher_required
def get_weeks(request):
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

@teacher_required
def week_last_date(request):
    """
    Manage the setting of the last date for a specific week by a teacher.

    This view allows a teacher to set the last date for a particular week in their course.
    The teacher must be logged in to access this functionality. If the request method is
    POST, it processes the submitted form data. If the form is valid, it saves the last date
    and records this action in the TeacherActivity log.

    Decorators:
    - @teacher_required: Ensures that only authenticated teachers can access this view.

    Request Types:
    - GET: Renders the form for setting the last date.
    - POST: Processes the submitted form data to set the last date.

    Parameters:
    - request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    - HttpResponse: Renders the 'teachers/week_last_date.html' template with the form for
      GET requests or redirects to the same page with a success message for POST requests.

    Example Usage:
    - A teacher accesses the "Set Last Date" page, fills in the last date for a specific week,
      and submits the form. Upon successful submission, a confirmation message is displayed.
    """
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        return redirect('teacher_login')

    teacher = Teacher.objects.get(id=teacher_id)

    if request.method == 'POST':
        form = WeekLastDateForm(request.POST)
        if form.is_valid():
            week_date = form.save()

            TeacherActivity.objects.create(
                teacher=teacher,
                action='Set Last Date',
                course=week_date.course,
                semester=week_date.semester,
                week=week_date.week,
                description=week_date.last_date
            )

            messages.success(request, 'Last date set successfully')
            return redirect('week_last_date')
    else:
        form = WeekLastDateForm()

    return render(request, 'teachers/week_last_date.html', {'form': form})

@teacher_required
@require_GET
def fetch_student_details(request):
    """
    Fetch and return detailed student information, including progress on problems and commits.

    This view is designed to be accessed by teachers to retrieve specific details of a student's
    progress. It provides an overview of the student's course and semester information, the number
    of problems solved, commit history for each week, and the status of commits (whether they were
    on time or late).

    Decorators:
    - @teacher_required: Ensures that only authenticated teachers can access this view.
    - @require_GET: Restricts the view to accept only GET requests.

    Parameters:
    - request (HttpRequest): The HTTP request object containing the GET parameters.

    GET Parameters:
    - faculty_number: The student's faculty number, used to identify the student.

    Returns:
    - JsonResponse: A JSON object containing the student's details, including:
        - name (str): The student's first and last name.
        - enrollment_number (str): The student's enrollment number.
        - faculty_number (str): The student's faculty number.
        - course (str): The student's course.
        - semester (str): The student's current semester.
        - available_weeks (list): A list of weeks for which problems are available.
        - problem_solved_overall (int): Total number of problems solved by the student.
        - problems_solved_weekly (list): A list of problems solved per week.
        - last_commit_times (list): A list of the last commit times and commit hashes for each week.
        - total_problems (list): A list of total problems available per week.
        - statuses (list): A list of commit statuses, indicating whether the submission was on time or late.

    Raises:
    - JsonResponse: Returns a 404 status with an error message if the student with the provided
      faculty number does not exist.

    Example Usage:
    - A teacher submits a GET request with the 'faculty_number' as a query parameter, and the view
      returns a JSON response with detailed information about the student's problem-solving progress
      and commit history.
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
        week_last = WeekLastDate.objects.filter(course=student.course, semester=student.semester, week=week_number).first()
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

@teacher_required
def check_student_details(request):
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
    return render(request, 'teachers/check_student_details.html')

@teacher_required
@csrf_exempt
@require_POST
def log_activity(request):
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
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        return JsonResponse({'error': 'Teacher not logged in'}, status=404)

    teacher = Teacher.objects.get(id=teacher_id)
    action = request.POST.get('action')
    course = request.POST.get('course')
    semester = request.POST.get('semester')
    week = request.POST.get('week')

    TeacherActivity.objects.create(
        teacher=teacher,
        action=action,
        course=course,
        semester=semester,
        week=week
    )

    return JsonResponse({'success': 'Activity logged successfully'})


@teacher_required
@require_GET
def fetch_whole_class_weekly(request):
    """
    Retrieve weekly progress data for an entire class.

    This view fetches detailed weekly reports for all students in a particular course and semester.
    It returns data on each student's weekly problem-solving progress, last commit time, and whether
    their submission was on time or late, based on the last commit date and the set week deadline.

    Decorators:
    - @teacher_required: Ensures that only authenticated teachers can access this view.
    - @require_GET: Restricts access to GET requests only.

    Parameters:
    - request (HttpRequest): The HTTP request object, expected to contain GET parameters:
        - 'course' (str): The course identifier.
        - 'semester' (str): The semester identifier.
        - 'week' (str): The specific week for which the report is being fetched.

    Returns:
    - JsonResponse: A JSON array containing student report data, with each entry having:
        - 'enrollment_number' (str): The student's enrollment number.
        - 'faculty_number' (str): The student's faculty number.
        - 'full_name' (str): The student's full name.
        - 'last_commit_time' (str or datetime): The time of the student's last commit for the given week.
        - 'problems_solved' (int): The number of problems the student solved in the given week.
        - 'total_problems' (int): The total number of problems assigned in the week.
        - 'status' (str): The submission status, either 'On Time', 'Late', or 'No Commits'.

    Process:
    - Fetches all students enrolled in the given course and semester.
    - Retrieves the set last date for submissions for the specified week.
    - For each student, it checks their problem-solving progress for the week, last commit time, and
      whether their submission was made on time or late.
    - Returns the data in JSON format to be consumed by the frontend or other systems.

    Example Response:
    [
        {
            'enrollment_number': '1234567890',
            'faculty_number': 'FAC123',
            'full_name': 'John Doe',
            'last_commit_time': '2024-09-20 10:30:00',
            'problems_solved': 3,
            'total_problems': 5,
            'status': 'On Time'
        },
        ...
    ]
    """
    course = request.GET.get('course')
    semester = request.GET.get('semester')
    week = request.GET.get('week')

    all_student = Student.objects.filter(course=course, semester=semester).order_by('faculty_number')

    # Fetch last date for the week
    week_last_date_2 = WeekLastDate.objects.filter(course=course, semester=semester, week=week).first()
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

@teacher_required
def check_whole_class_weekly(request):
    """
    Render the page for checking the weekly progress of the whole class.

    This view is responsible for rendering a template where teachers can view the weekly progress
    of all students in a class. The progress includes details such as the number of problems solved,
    last commit time, and submission status (on time or late).

    Decorators:
    - @teacher_required: Ensures that only authenticated teachers can access this view.

    Parameters:
    - request (HttpRequest): The HTTP request object that contains session data and is used to render the page.

    Returns:
    - HttpResponse: A response that renders the 'check_weekly_class.html' template, which allows the teacher
      to check class progress. The actual student data is fetched separately using the appropriate API endpoint.

    This view does not handle any data processing itself but serves as a front-end entry point for the
    teacher to interact with the system and fetch detailed reports using JavaScript or other mechanisms
    from the frontend.

    Example:
    When a teacher visits this page, they can select the course, semester, and week they want to view.
    The page will then display the weekly report, which will likely be fetched via AJAX or similar methods
    using endpoints such as `fetch_whole_class_weekly`.
    """
    return render(request, 'teachers/check_weekly_class.html')


@teacher_required
@require_GET
def fetch_whole_class(request):
    """
    Fetch the progress report for all students in a given course and semester.

    This view retrieves detailed information about each student's weekly progress in a specific course
    and semester. It includes data such as the number of problems solved, total problems, last commit time,
    and the commit status for each week.

    Decorators:
    - @teacher_required: Ensures that only authenticated teachers can access this view.
    - @require_GET: Restricts the view to only accept GET requests.

    Parameters:
    - request (HttpRequest): The HTTP request object containing query parameters 'course' and 'semester'.

    Query Parameters:
    - course (str): The course for which to retrieve student data.
    - semester (str): The semester for which to retrieve student data.

    Returns:
    - JsonResponse: A JSON object containing detailed progress data for all students in the course and semester.
      The structure of the JSON response includes:
        - enrollment_number: The student's enrollment number.
        - faculty_number: The student's faculty number.
        - name: The student's full name.
        - weeks_data: A list of dictionaries containing data for each week, including:
            - week: The week number.
            - total_problems: Total number of problems available in that week.
            - problems_solved: Number of problems solved by the student.
            - last_commit_time: The timestamp of the last commit for that week.
            - commit_status: The submission status (On Time, Late, No Commits).

    The `available_weeks` list is generated by filtering the `Problem` model to determine which weeks have
    assigned problems for the given course and semester. For each student, the following information is gathered:
    - Problems solved per week (from the `ProblemCompletion` model).
    - Last commit time and status (from the `WeekCommit` model).
    - Deadline for the week's submission (from the `WeekLastDate` model).

    Example JSON response:
    [
        {
            'enrollment_number': '1234567890',
            'faculty_number': 'FAC12345',
            'name': 'John Doe',
            'weeks_data': [
                {
                    'week': 1,
                    'total_problems': 10,
                    'problems_solved': 7,
                    'last_commit_time': '2024-09-30 12:34:56',
                    'commit_status': 'On Time'
                },
                ...
            ]
        },
        ...
    ]

    The response data is structured to provide a comprehensive overview of the student's progress for each
    available week, allowing teachers to track both individual and class-wide performance.

    Raises:
    - JsonResponse with an empty list if no students or problems are found for the given course and semester.
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
            week_last = WeekLastDate.objects.filter(course=course, semester=semester, week=week).first()
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

@teacher_required
def check_whole_class(request):
    """
    Render the 'Check Whole Class' page for teachers.

    This view serves as the interface for teachers to check the performance of all students in a given course
    and semester. It renders a template that allows teachers to select the course and semester and view
    a detailed report of the entire class's progress over available weeks.

    Decorators:
    - @teacher_required: Ensures that only authenticated teachers can access this view.

    Parameters:
    - request (HttpRequest): The HTTP request object.

    Template:
    - 'teachers/check_whole_class.html': The HTML template that presents the interface for checking the
      whole class's performance.

    Returns:
    - HttpResponse: Renders the 'check_whole_class.html' template for the teacher to interact with.

    Usage:
    This view is typically used in conjunction with `fetch_whole_class`, which provides the data about
    students' progress. The page rendered by this view will use that data to display the report.

    Example:
    When the teacher accesses this page, they will be able to choose from available courses and semesters,
    and the system will display a report summarizing the class's progress.
    """
    return render(request, 'teachers/check_whole_class.html')


@teacher_required
@csrf_exempt
@require_POST
def trigger_update(request):
    """
    Triggers the update of student problem completion and commit data for a specific course and semester.

    This view allows a teacher to initiate an update for student data based on their GitHub repositories.
    The update is restricted to once per hour to avoid excessive API calls or accidental re-triggering.

    Restrictions:
    - A teacher must be logged in and have their `teacher_id` stored in the session.
    - The update process can only be triggered if it has been at least one hour since the last update.

    Parameters:
    - `course` (POST): The course for which the data update is triggered.
    - `semester` (POST): The semester for which the data update is triggered.

    Behavior:
    - The function checks the timestamp of the last update (if any) and compares it to the current time.
    - If less than an hour has passed since the last update, the function returns an error response, disabling the button.
    - If more than an hour has passed, the function triggers the `update_student_data()` process and logs the activity
      in the `TeacherActivity` model.

    Response:
    - On success, returns a JSON response with the message 'Data updated successfully'.
    - On failure (if the teacher is not logged in or if the update has been triggered within the last hour),
      it returns an error response with relevant details.

    Example usage:
    ```
    POST /trigger_update/
    {
        "course": "CS101",
        "semester": "Fall2024"
    }
    ```
    Example response:
    ```
    {
        "success": "Data updated successfully"
    }
    ```

    Error response (if triggered within the last hour):
    ```
    {
        "error": "Button is disabled for 1 hour because [Teacher Name] updated for [Course], Semester [Semester]"
    }
    ```

    Error response (if teacher is not logged in):
    ```
    {
        "error": "Teacher not logged in"
    }
    ```

    External Dependencies:
    - This view relies on the `update_student_data()` function to handle the actual update process.
    - `TeacherActivity` model is used to log the teacher's actions and prevent multiple triggers within a short period.

    Notes:
    - CSRF protection is disabled due to the use of `@csrf_exempt`.
    """
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        return JsonResponse({'error': 'Teacher not logged in'}, status=404)

    last_update = TeacherActivity.objects.filter(action='Updated the data').order_by('-timestamp').first()

    # Check if the last update was within the past hour
    if last_update and (timezone.now() - last_update.timestamp) < timedelta(hours=1):
        return JsonResponse({
            'error': f'Button is disabled for 1 hour because {last_update.teacher} updated for {last_update.course}, Semester {last_update.semester}'
        })

    teacher = Teacher.objects.get(id=teacher_id)
    course = request.POST.get('course')
    semester = request.POST.get('semester')

    # Call the function to update student data based on the selected course and semester
    update_student_data(course, semester)

    # Log the teacher's activity
    TeacherActivity.objects.create(
        teacher=teacher,
        action='Updated the data',
        course=course,
        semester=semester,
    )

    return JsonResponse({'success': 'Data updated successfully'})

@teacher_required
@require_GET
def delete_old_students(request):
    """
    View for deleting students who have been inactive for over 150 days.
    The view can only be accessed by teachers and performs a number of checks
    before proceeding with the deletion.

    Process:
    1. Verify that the teacher is logged in by checking the session data.
    2. Check whether a new semester has been started in the past 150 days.
    3. If no recent semester has started, identify students who have been on
       the platform for more than 150 days, excluding any 'dummy' students and superusers.
    4. Delete the eligible students and log the action as a new semester started.

    Parameters:
        request (HttpRequest): The incoming request object, must be a GET request.

    Returns:
        JsonResponse: A JSON response indicating the result of the operation:
        - Error if no teacher is logged in.
        - Error if a new semester has been started within the last 150 days.
        - Error if no students are found who are eligible for deletion.
        - Success message with the number of students deleted.

    Decorators:
        @teacher_required: Ensures the view is only accessible to logged-in teachers.
        @require_GET: Restricts the view to only accept GET requests.
    """
    # Get the teacher ID from session
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        # Return an error if the teacher is not logged in
        return JsonResponse({'error': 'Teacher not logged in'}, status=404)

    # Get the teacher object based on session ID
    teacher = Teacher.objects.get(id=teacher_id)

    # Define the cutoff date (150 days from the current time)
    cutoff_date = timezone.now() - timedelta(days=150)

    # Check if a new semester has been started in the last 150 days
    recent_activity_exists = TeacherActivity.objects.filter(
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
    TeacherActivity.objects.create(
        teacher=teacher,
        action='Started a New Semester',
    )

    # Return a success response with the number of deleted students
    return JsonResponse({'success': f'{num_deleted} students deleted successfully'})

@teacher_required
def your_activity(request):
    """
    View for displaying a teacher's recent activities in a paginated format.
    The activities include actions such as adding or editing problems, viewing or downloading
    class reports, starting a new semester, and updating course data.

    Process:
    1. Check if the teacher is logged in by verifying the session data.
    2. Retrieve all activities performed by the logged-in teacher, sorted in reverse chronological order.
    3. Format each activity for readability, displaying details such as the course, semester, week, and action performed.
    4. Paginate the activities with 15 activities per page.
    5. Render the activity list in the 'teachers/your_activity.html' template.

    Parameters:
        request (HttpRequest): The incoming request object.

    Returns:
        JsonResponse: If the teacher is not logged in, an error is returned in JSON format.
        HttpResponse: Renders the 'teachers/your_activity.html' template with the teacher's activities.

    Decorators:
        @teacher_required: Ensures the view is only accessible to logged-in teachers.
    """

    # Get the teacher ID from the session
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        # Return an error if the teacher is not logged in
        return JsonResponse({'error': 'Teacher not logged in'})

    # Get the teacher object based on the session ID
    teacher = Teacher.objects.get(id=teacher_id)

    # Retrieve all activities of the teacher, sorted by timestamp (most recent first)
    all_activity = TeacherActivity.objects.filter(teacher=teacher).order_by('-timestamp')

    def format_activity2(activity):
        """
        Helper function to format a single activity into a readable string.

        Parameters:
            activity (TeacherActivity): The activity object to format.

        Returns:
            str: A formatted string describing the activity, including the timestamp, action, course, semester, and description.
        """
        # Format the timestamp in a readable format
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
        'teacher': teacher,
        'page_obj': page_obj
    }

    # Render the activity page
    return render(request, 'teachers/your_activity.html', context)

@teacher_required
def other_activity(request):
    """
    View for displaying activities performed by other teachers in a paginated format.
    The activities include actions such as adding or editing problems, viewing or downloading
    class reports, starting a new semester, and updating course data.

    Process:
    1. Check if the current teacher is logged in by verifying session data.
    2. Retrieve all activities performed by other teachers, excluding the current teacher, sorted in reverse chronological order.
    3. Format each activity for readability, displaying details such as the course, semester, week, action performed, and the teacher's name.
    4. Paginate the activities with 15 activities per page.
    5. Render the activity list in the 'teachers/other_activity.html' template.

    Parameters:
        request (HttpRequest): The incoming request object.

    Returns:
        JsonResponse: If the teacher is not logged in, an error is returned in JSON format.
        HttpResponse: Renders the 'teachers/other_activity.html' template with other teachers' activities.

    Decorators:
        @teacher_required: Ensures the view is only accessible to logged-in teachers.
    """

    # Get the teacher ID from the session
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        # Return an error if the teacher is not logged in
        return JsonResponse({'error': 'Teacher not logged in'})

    # Get the teacher object based on session ID
    teacher = Teacher.objects.get(id=teacher_id)

    # Retrieve all activities performed by other teachers, ordered by timestamp (most recent first)
    other_teacher_activities = TeacherActivity.objects.exclude(teacher=teacher).order_by('-timestamp')

    def format_activity(activity):
        """
        Helper function to format a single activity into a readable string, including
        the teacher's name and the details of the action performed.

        Parameters:
            activity (TeacherActivity): The activity object to format.

        Returns:
            str: A formatted string describing the activity, including the timestamp, action, teacher's name, course, semester, and description.
        """
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
    return render(request, 'teachers/other_activity.html', context)
