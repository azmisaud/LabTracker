from django.shortcuts import render, redirect
from students.forms import StudentSignUpForm


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
