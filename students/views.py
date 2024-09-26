from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from LabTrackerAMU.decorators import student_required
from problems.models import WeekCommit, ProblemCompletion, Problem
from students.forms import StudentSignUpForm
from django.contrib.auth import login as auth_login, logout
from teachers.models import WeekLastDate


def student_signup(request):
    """
    Handles the student sign-up view.

    - If the request method is POST, it processes the submitted form.
      If the form is valid, the user is saved and the page is redirected to the 'student_signup' view.
    - If the form is invalid, the form is re-rendered with validation errors.
    - If the request method is GET, an empty form is displayed for user input.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the student sign-up page with either an empty form or form with errors.
    """
    # Handle form submission if the request is a POST
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)

        # Check if the form data is valid
        if form.is_valid():
            # Save the user and create the student account
            user = form.save()
            # Redirect to the same page (or another) upon successful sign-up
            return redirect('student_signup')
        else:
            # If the form is invalid, re-render the page with form errors
            return render(request, 'students/signup.html', {'form': form})

    # For GET requests, create an empty form
    else:
        form = StudentSignUpForm()

    # Render the sign-up template with the form
    return render(request, 'students/signup.html', {'form': form})


def student_login(request):
    """
    Handle the login process for students using Django's AuthenticationForm.

    This view function checks if the incoming request is a POST request (i.e., the login form has been submitted).
    If the form submission is valid, it authenticates and logs in the user. If the request method is not POST,
    the function renders a blank login form.

    Args:
        request: HttpRequest object that contains metadata about the request.

    Returns:
        HttpResponseRedirect: Redirects to the 'student_dashboard' page upon successful login.
        HttpResponse: Renders the login page with the AuthenticationForm if GET request or invalid POST data.

    Flow:
    - If the request method is POST:
        - Instantiate the AuthenticationForm with the POST data.
        - Validate the form. If valid:
            - Get the user object.
            - Authenticate and log in the user.
            - Redirect the logged-in user to the 'student_dashboard' page.
    - If the request method is GET:
        - Instantiate an empty AuthenticationForm and render the login page.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('student_dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'students/login.html', {'form': form})


def student_logout(request):
    """
    Logs out the current student and redirects them to the login page.

    This view function is responsible for logging out the currently authenticated student
    by calling Django's built-in `logout` function, which clears the session data.
    Once logged out, the user is redirected to the student login page.

    Args:
        request (HttpRequest): The incoming HTTP request object that triggers the logout.

    Returns:
        HttpResponseRedirect: A redirect to the 'student_login' view after the student is logged out.

    Example Usage:
        A student clicking the "logout" button will trigger this view. Upon execution:
        - The student will be logged out, clearing their session and authentication data.
        - The student will be redirected to the login page where they can log in again.

    Notes:
        - This function uses Django's `logout` function to handle the actual session clearing and user logout.
        - No special permissions are required to access this view since it is typically triggered by authenticated users.
    """

    # Call Django's built-in logout function to clear the user's session and authentication data
    logout(request)

    # Redirect the user to the student login page after logout
    return redirect('student_login')


@student_required
def student_dashboard(request):
    """
    Handles the student dashboard view. Provides an overview of the student's progress
    by retrieving problems assigned to their course and semester, their completion status,
    weekly commits, and deadlines. The overall progress is calculated as well as weekly
    progress.

    Parameters:
    request (HttpRequest): The HTTP request object which contains the logged-in student.

    Returns:
    HttpResponse: The rendered 'students/dashboard.html' template with the student's progress data.
    """

    # Retrieve the logged-in student and their course and semester information
    student = request.user
    course = student.course
    semester = student.semester

    # Fetch problems for the student's course and semester, ordered by week and problem number
    problems = Problem.objects.filter(course=course, semester=semester).order_by('week', 'problemNumber')

    # Fetch the student's completion records for the filtered problems
    problem_completions = ProblemCompletion.objects.filter(student=student, problem__in=problems).order_by('problem')

    # Fetch WeekCommit entries for the student, ordered by week number
    week_commits = WeekCommit.objects.filter(student=student).order_by('week_number')

    # Convert week commit data into a dictionary for easy access by week number
    week_commit_data = {week_commit.week_number: week_commit for week_commit in week_commits}

    # Fetch deadlines (last dates) for each week of the student's course and semester
    week_last_dates = WeekLastDate.objects.filter(course=course, semester=semester)

    # Store week deadlines in a dictionary for quick lookup by week number
    week_last_date_data = {week_last.week: week_last.last_date for week_last in week_last_dates}

    # Initialize dictionaries to track weekly and overall progress
    weekly_progress = {}
    overall_progress = {'total': len(problems), 'completed': 0}

    # List to store the completion status of each problem for rendering purposes
    completion_list = []

    # Loop through each problem and calculate the student's progress
    for prob in problems:
        week = prob.week

        # Initialize weekly progress if it hasn't been done for the current week
        if week not in weekly_progress:
            weekly_progress[week] = {
                'total': 0,
                'completed': 0,
                'last_commit_time': None,
                'last_commit_hash': None,
                'last_date': week_last_date_data.get(week, 'No Deadline')  # Provide deadline if available
            }

        # Increment the total number of problems for the current week
        weekly_progress[week]['total'] += 1

        # Check if the current problem is completed by the student
        completion = problem_completions.filter(problem=prob).first()
        is_completed = completion and completion.is_completed

        # Append the completion status for the current problem
        completion_list.append({
            'problem_id': prob.id,
            'is_completed': is_completed
        })

        # If the problem is completed, update weekly and overall progress
        if is_completed:
            weekly_progress[week]['completed'] += 1
            overall_progress['completed'] += 1

        # If commit data is available for the week, update the last commit information
        if week in week_commit_data:
            week_commit = week_commit_data[week]
            weekly_progress[week]['last_commit_time'] = week_commit.last_commit_time
            weekly_progress[week]['last_commit_hash'] = week_commit.last_commit_hash

    # Calculate the overall completion percentage (avoid division by zero)
    overall_progress['percentage'] = (
        (overall_progress['completed'] / overall_progress['total']) * 100
        if overall_progress['total'] > 0
        else 0
    )

    # Prepare the context for rendering the template
    context = {
        'student': student,
        'weekly_progress': weekly_progress,  # Progress for each week
        'overall_progress': overall_progress,  # Overall progress across all weeks
        'problems': problems,  # List of problems for the course
        'completion_list': completion_list,  # Completion status for each problem
    }

    # Render and return the student dashboard template with the context data
    return render(request, 'students/dashboard.html', context)
