from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render, get_object_or_404, redirect

from LabTrackerAMU.decorators import teacher_required
from teachers.models import Teacher, TeacherActivity
from .models import Problem
from .forms import ProblemForm


@teacher_required
def add_problem(request):
    """
    Handles the process of adding a new problem by a teacher.

    This view ensures that only authenticated teachers can add problems and records the action in the
    TeacherActivity model.

    Flow:
    - Checks if the teacher is logged in via session data (`teacher_id`). If not, redirects to the login page.
    - Processes a POST request to handle form submission for adding a problem.
    - If the form is valid, saves the problem, logs the action in the `TeacherActivity` model, and redirects to the problem addition page with a success message.
    - For a GET request, renders the empty `ProblemForm` for problem creation.

    Args:
        request (HttpRequest): The HTTP request object, either GET or POST.

    Returns:
        HttpResponse: Renders the problem addition form on GET request or redirects on successful form submission.

    Raises:
        Redirects to 'teacher_login' if the teacher is not authenticated (no `teacher_id` in the session).
    """

    # Get the teacher_id from session to verify if the teacher is logged in
    teacher_id = request.session.get('teacher_id')

    # If the teacher is not logged in, redirect to the login page
    if not teacher_id:
        return redirect('teacher_login')

    # Retrieve the Teacher object based on the session's teacher_id
    teacher = Teacher.objects.get(id=teacher_id)

    # Handle POST request when the teacher submits the problem form
    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)

        # Validate the form data
        if form.is_valid():
            # Save the new problem
            problem = form.save()

            # Log the teacher's activity in the TeacherActivity model
            TeacherActivity.objects.create(
                teacher=teacher,
                action='Added Problem',
                course=problem.course,
                semester=problem.semester,
                week=problem.week,
                description=problem.description,
            )

            # Show a success message and redirect back to the add problem page
            messages.success(request, 'PROBLEM ADDED SUCCESSFULLY')
            return redirect('addProblem')

    # If GET request or invalid form, render the form again
    else:
        form = ProblemForm()

    # Render the add problem template with the form
    return render(request, 'problems/addproblem.html', {'form': form})



