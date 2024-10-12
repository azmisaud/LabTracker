from django.urls import path
from . import views

urlpatterns = [
    path('addProblem/',views.add_problem, name='addProblem'),
    path('editProblem/',views.edit_problem, name='create_problem'),
    path('api/get_semesters/', views.get_semesters, name='get_semesters'),
    path('api/get_weeks/', views.get_weeks, name='get_weeks'),
    path('api/get_problems/', views.get_problems, name='get_problems'),
    path('api/get_problem_details/', views.get_problem_details, name='get_problem_details'),
]