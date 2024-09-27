from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.student_signup, name='student_signup'),
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='student_logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('download-index/',views.generate_problem_doc,name='generate_problem_doc'),
]