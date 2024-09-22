from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import TeacherLoginForm
from .models import Teacher
from LabTrackerAMU.decorators import teacher_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from students.models import Student
from problems.models import Problem

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
