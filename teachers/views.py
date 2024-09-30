from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import TeacherLoginForm, WeekLastDateForm
from .models import Teacher, TeacherActivity, WeekLastDate
from LabTrackerAMU.decorators import teacher_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from students.models import Student
from problems.models import Problem, ProblemCompletion, WeekCommit


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
