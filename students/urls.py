from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.student_signup, name='student_signup'),
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='student_logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('download-index/',views.generate_problem_doc,name='generate_problem_doc'),
    path('generate-file/<int:week>/', views.generate_file, name='generate_file'),
    path('first-step/',views.forgot_password,name='forgot_password'),
    path('second-step/',views.verify_date_of_birth,name='verify_date_of_birth'),
    path('third-step/',views.reset_password,name='reset_password'),
    path('forgot-password/',views.password_reset,name='password_reset'),
]