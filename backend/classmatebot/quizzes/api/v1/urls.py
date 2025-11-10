from django.urls import path

from rest_framework.schemas import get_schema_view

from . import views

schema_view = get_schema_view(title='Quizzes API')

app_name = 'quizzes'
urlpatterns = [
    path('quizzes/', views.QuizListCreateView.as_view()),
    path('quizzes/<int:pk>/', views.QuizRetrieveUpdateView.as_view()),
]