from functools import wraps
from django.shortcuts import redirect
from students.models import Student
from teachers.models import Teacher

def student_required(view_func):
    """
    Decorator to restrict access to views for authenticated students only.

    This decorator ensures that the decorated view can only be accessed by
    users who are authenticated as `Student` instances. If the user is not
    authenticated or is not a student, they are redirected to the student
    login page.

    Args:
        view_func (function): The view function that is being decorated.

    Returns:
        function: A wrapped view function that either processes the request
        for authenticated students or redirects unauthenticated users
        to the login page.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        """
        Inner function to check if the user is an authenticated student.

        If the user is authenticated and is an instance of the `Student` model,
        the original view function is executed. Otherwise, the user is
        redirected to the student login page.

        Args:
            request (HttpRequest): The HTTP request object, containing
            information about the current request.
            *args: Variable length argument list for the view.
            **kwargs: Arbitrary keyword arguments for the view.

        Returns:
            HttpResponse: The original view for authenticated students,
            or a redirect response for unauthorized users.
        """
        # Check if the user is authenticated and is a student.
        if request.user.is_authenticated and isinstance(request.user, Student):
            return view_func(request, *args, **kwargs)
        else:
            # Redirect unauthorized users to the student login page.
            return redirect('student_login')

    return _wrapped_view

def teacher_required(view_func):
    """
    Decorator to restrict access to views for authenticated teachers only.

    This decorator ensures that the decorated view can only be accessed by
    users who have a valid teacher session. If the session does not contain
    the 'teacher_id', the user is redirected to the teacher login page.

    Args:
        view_func (function): The view function that is being decorated.

    Returns:
        function: A wrapped view function that processes the request for
        authenticated teachers or redirects unauthorized users to the
        login page.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        """
        Inner function to check if the user has a valid teacher session.

        If the session contains 'teacher_id', it means the user is authenticated
        as a teacher and the original view function is executed. If not,
        the user is redirected to the teacher login page.

        Args:
            request (HttpRequest): The HTTP request object, containing
            information about the current request.
            *args: Variable length argument list for the view.
            **kwargs: Arbitrary keyword arguments for the view.

        Returns:
            HttpResponse: The original view for authenticated teachers,
            or a redirect response to the login page for unauthorized users.
        """
        # Check if the session contains a valid 'teacher_id'.
        if request.session.get('teacher_id'):
            # Call the original view function if the user is authenticated as a teacher.
            return view_func(request, *args, **kwargs)
        else:
            # Redirect unauthorized users to the teacher login page.
            return redirect('teacher_login')

    return _wrapped_view
