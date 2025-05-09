from django.urls import path
from . import views


urlpatterns = [
    path('login/',views.instructor_login,name='instructor_login'),
    path('change_password/',views.instructor_change_password,name='instructor_change_password'),
    path('get-semesters/',views.get_semesters_instructor,name='get_semesters_instructors'),
    path('get-students/',views.get_students_for_mentorship,name='get_students_for_mentorship'),
    path('save-selected-students/',views.save_selected_students,name='save_selected_students'),
    path('select-students/',views.select_students,name='select_students'),
    path('dashboard/',views.instructor_dashboard,name='instructor_dashboard'),
    path('feedback/<int:submission_id>/',views.submit_feedback,name='submit_feedback'),
    path('logout/',views.instructor_logout,name='instructor_logout'),
]