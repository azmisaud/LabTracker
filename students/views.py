from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from students.forms import StudentSignUpForm
from django.contrib.auth import login as auth_login, logout

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
            return redirect('student_login')
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
