from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.teacher_login,name='teacher_login'),
]