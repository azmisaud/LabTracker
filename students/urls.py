from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.student_signup, name='student_signup'),
    path('login/', views.student_login, name='student_login'),
]