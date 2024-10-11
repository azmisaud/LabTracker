from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.faculty_login,name='faculty_login'),
    path('change_password/',views.change_password,name='change_password'),
    path('logout/',views.faculty_logout,name='faculty_logout'),
    path('set-last-date/',views.week_last_date_faculty,name='week_last_date_faculty'),
    path('get-semesters/',views.get_semesters_faculty,name='get_semesters_faculty'),
    path('get-weeks/',views.get_weeks_faculty,name='get_weeks_faculty'),
    path('get-faculty-numbers/',views.get_faculty_numbers_faculty,name='get_faculty_numbers_faculty'),
    path('fetch-student-details/',views.fetch_student_details_faculty,name='fetch_student_details_faculty'),
    path('check-student-details/',views.check_student_details_faculty,name='check_student_details_faculty'),
    path('log_activity/', views.log_activity_faculty, name='log_activity_faculty'),
    path('fetch-whole-class-weekly/', views.fetch_whole_class_weekly_faculty, name='fetch_whole_class_weekly_faculty'),
    path('check-whole-class-weekly/', views.check_whole_class_weekly_faculty, name='check_whole_class_weekly_faculty'),
    path('fetch-whole-class/', views.fetch_whole_class_faculty, name='fetch_whole_class_faculty'),
    path('check-whole-class/', views.check_whole_class_faculty, name='check_whole_class_faculty'),
    path('trigger-update/', views.trigger_update_faculty, name='trigger_update_faculty'),
    path('start-new/', views.delete_old_students_faculty, name='start_a_new_semester'),
    path('your-activities/', views.your_activity_faculty, name='your_activities_faculty'),
    path('other-activities/', views.other_activity_faculty, name='other_activities'),
    path('fetch-graph-data/', views.fetch_graph_data_faculty, name='fetch_graph_data'),
    path('dashboard/', views.faculty_dashboard, name='faculty_dashboard'),

]