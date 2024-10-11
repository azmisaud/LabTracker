from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render, get_object_or_404, redirect
from LabTrackerAMU.decorators import faculty_required
from faculty.models import FacultyActivity
from .models import Problem
from .forms import ProblemForm


def add_problem(request):

    faculty=request.user

    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)

        # Validate the form data
        if form.is_valid():
            # Save the new problem
            problem = form.save()

            FacultyActivity.objects.create(
                faculty=faculty,
                action='Added Problem',
                course=problem.course,
                semester=problem.semester,
                week=problem.week,
                description=problem.description,
            )

            messages.success(request, 'PROBLEM ADDED SUCCESSFULLY')
            return redirect('addProblem')

    # If GET request or invalid form, render the form again
    else:
        form = ProblemForm()

    # Render the add problem template with the form
    return render(request, 'problems/addproblem.html', {'form': form})


@require_GET
def get_semesters(request):
    """
    Retrieves distinct semesters for a given course in the Problem model.

    This view is restricted to GET requests and responds with a list of unique semesters associated
    with the specified course, as provided through the request's query parameters. It returns a JSON
    response containing the list of semesters.

    Flow:
    - Extracts the `course` parameter from the GET request.
    - Queries the `Problem` model to find distinct semesters for the given course.
    - Returns the distinct semester values as a JSON response.

    Args:
        request (HttpRequest): The incoming HTTP GET request containing a 'course' parameter.

    Returns:
        JsonResponse: A JSON response containing the list of distinct semesters for the specified course.

    Example Usage:
        GET /get-semesters/?course=BCA
        Response: {"semesters": [1, 2, 3]}
    """

    # Extract the 'course' parameter from the GET request
    course = request.GET.get('course')

    # Query the Problem model to find distinct semesters for the given course
    semesters = Problem.objects.filter(course=course).values_list('semester', flat=True).distinct()

    # Return the semesters as a JSON response
    return JsonResponse({'semesters': list(semesters)})


@require_GET
def get_weeks(request):
    """
    Retrieves distinct weeks for a specified course and semester from the Problem model.

    This view handles GET requests to return a list of unique week numbers based on the course and semester
    specified in the query parameters. It responds with a JSON object containing the list of weeks.

    Flow:
    - Extracts the `course` and `semester` parameters from the GET request.
    - Queries the `Problem` model to find distinct week numbers associated with the given course and semester.
    - Returns the unique week numbers as a JSON response.

    Args:
        request (HttpRequest): The incoming HTTP GET request containing `course` and `semester` parameters.

    Returns:
        JsonResponse: A JSON response containing the list of distinct week numbers for the specified course and semester.

    Example Usage:
        GET /get-weeks/?course=BCA&semester=3
        Response: {"weeks": [1, 2, 3, 4]}

    Raises:
        ValueError: If invalid or missing query parameters are provided, though currently no error handling is implemented.
    """

    # Extract the 'course' and 'semester' parameters from the GET request
    course = request.GET.get('course')
    semester = request.GET.get('semester')

    # Query the Problem model to find distinct weeks for the given course and semester
    weeks = Problem.objects.filter(course=course, semester=semester).values_list('week', flat=True).distinct()

    # Return the weeks as a JSON response
    return JsonResponse({'weeks': list(weeks)})


@require_GET
def get_problems(request):
    """
    Retrieves distinct problem numbers for a specified course, semester, and week from the Problem model.

    This view handles GET requests to return a list of unique problem numbers based on the course, semester,
    and week specified in the query parameters. It responds with a JSON object containing the list of problem numbers.

    Flow:
    - Extracts the `course`, `semester`, and `week` parameters from the GET request.
    - Queries the `Problem` model to find distinct problem numbers associated with the given course, semester, and week.
    - Returns the unique problem numbers as a JSON response.

    Args:
        request (HttpRequest): The incoming HTTP GET request containing `course`, `semester`, and `week` parameters.

    Returns:
        JsonResponse: A JSON response containing the list of distinct problem numbers for the specified course, semester, and week.

    Example Usage:
        GET /get-problems/?course=BCA&semester=3&week=2
        Response: {"problems": [1, 2, 3]}

    Raises:
        ValueError: If invalid or missing query parameters are provided, though no explicit error handling is currently implemented.
    """

    # Extract 'course', 'semester', and 'week' parameters from the GET request
    course = request.GET.get('course')
    semester = request.GET.get('semester')
    week = request.GET.get('week')

    # Query the Problem model to find distinct problem numbers for the given course, semester, and week
    problems = Problem.objects.filter(course=course, semester=semester, week=week).values_list('problemNumber',
                                                                                               flat=True).distinct()

    # Return the problem numbers as a JSON response
    return JsonResponse({'problems': list(problems)})


@require_GET
def get_problem_details(request):
    """
    Retrieves detailed information for a specific problem based on the course, semester, week, and problem number.

    This view handles GET requests and returns the description and image URL (if available) for a specified problem
    using the `course`, `semester`, `week`, and `problemNumber` parameters provided in the query string. If the problem
    is not found, an error message is returned.

    Flow:
    - Extracts `course`, `semester`, `week`, and `problemNumber` from the GET request.
    - Attempts to retrieve the problem from the `Problem` model.
    - If found, returns the problem description and image URL (if available) as a JSON response.
    - If not found, returns an error message in the response.

    Args:
        request (HttpRequest): The incoming HTTP GET request containing `course`, `semester`, `week`, and `problemNumber`.

    Returns:
        JsonResponse:
            - If the problem is found, a JSON response containing `description` and `image` of the problem.
            - If the problem is not found, a JSON response containing an error message.

    Example Usage:
        GET /get-problem-details/?course=BCA&semester=3&week=2&problemNumber=1
        Response:
        {
            "success": True,
            "problem": {
                "description": "Solve the quadratic equation...",
                "image": "http://example.com/media/problems/image1.png"
            }
        }

        If the problem is not found:
        {
            "success": False,
            "error": "Problem not found."
        }

    Raises:
        Problem.DoesNotExist: If no problem matches the provided parameters, handled by returning an error in the response.
    """

    # Extract the required parameters from the GET request
    course = request.GET.get('course')
    semester = request.GET.get('semester')
    week = request.GET.get('week')
    problem_number = request.GET.get('problemNumber')

    try:
        # Retrieve the problem from the Problem model based on the provided course, semester, week, and problem number
        problem = Problem.objects.get(course=course, semester=semester, week=week, problemNumber=problem_number)

        # Prepare response data if the problem is found
        response_data = {
            'success': True,
            'problem': {
                'description': problem.description,
                'image': problem.image.url if problem.image else None,
            }
        }
    except Problem.DoesNotExist:
        # Handle case where the problem is not found
        response_data = {'success': False, 'error': 'Problem not found.'}

    # Return the response data as a JSON response
    return JsonResponse(response_data)


@faculty_required
def edit_problem(request):

    faculty=request.user
    problem = None  # Default value for problem (used in case the request method is GET)

    if request.method == 'POST':
        # Get the problem details from the form submission
        course = request.POST.get('course')
        semester = request.POST.get('semester')
        week = request.POST.get('week')
        problem_number = request.POST.get('problemNumber')

        # Retrieve the specific problem using the provided course, semester, week, and problem number
        problem = get_object_or_404(Problem, course=course, semester=semester, week=week, problemNumber=problem_number)

        # Initialize the form with the POST data and the current problem instance for editing
        form = ProblemForm(request.POST, request.FILES, instance=problem)

        if form.is_valid():
            # Save the edited problem
            form.save()

            # Log the teacher's activity of editing the problem
            FacultyActivity.objects.create(
                faculty=faculty,
                action='Edited Problem',
                course=problem.course,
                semester=problem.semester,
                week=problem.week,
                description=problem.description,
            )

            # Display a success message and redirect the user to the 'create_problem' page
            messages.success(request, 'PROBLEM EDITED SUCCESSFULLY')
            return redirect('create_problem')
    else:
        # If not POST, initialize an empty form for GET requests
        form = ProblemForm()

    # Render the edit problem page with the form and the problem details
    return render(request, 'problems/editproblem.html', {'form': form, 'problem': problem})
