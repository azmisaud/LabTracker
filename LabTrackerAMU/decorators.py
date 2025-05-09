from functools import wraps
from django.shortcuts import redirect
from faculty.models import Faculty
from instructor.models import Instructor
from students.models import Student

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and isinstance(request.user, Student):
            return view_func(request, *args, **kwargs)
        else:
            # Redirect unauthorized users to the student login page.
            return redirect('student_login')

    return _wrapped_view

def faculty_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and isinstance(request.user, Faculty):
            return view_func(request, *args, **kwargs)
        else:
            # Redirect unauthorized users to the faculty login page.
            return redirect('faculty_login')

    return _wrapped_view

def instructor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and isinstance(request.user, Instructor):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('instructor_login')

    return _wrapped_view