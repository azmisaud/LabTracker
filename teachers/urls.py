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

]