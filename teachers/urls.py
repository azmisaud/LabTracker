from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.teacher_login,name='teacher_login'),
    path('logout/', views.teacher_logout, name='teacher_logout'),
    path('set-last-date/', views.week_last_date, name='week_last_date'),
    path('get-semesters/', views.get_semesters2, name='get_semesters'),
    path('get-faculty-numbers/', views.get_faculty_numbers, name='get_faculty_numbers'),
    path('get-week/', views.get_weeks, name='get_weeks'),
    path('set-last-date/', views.week_last_date, name='week_last_date'),
    path('fetch-student-details/', views.fetch_student_details, name='fetch_student_details'),
    path('check-student-details/', views.check_student_details, name='check_student_details'),
    path('log_activity/', views.log_activity, name='log_activity'),
    path('fetch-whole-class-weekly/', views.fetch_whole_class_weekly, name='fetch_whole_class_weekly'),
    path('check-whole-class-weekly/', views.check_whole_class_weekly, name='check_whole_class_weekly'),
    path('fetch-whole-class/', views.fetch_whole_class, name='fetch_whole_class'),
    path('check-whole-class/', views.check_whole_class, name='check_whole_class'),

]