from django.urls import path

from rest_framework.schemas import get_schema_view

from . import views

schema_view = get_schema_view(title='Subjects API')

app_name = 'subjects'
urlpatterns = [
    path('subjects/', views.SubjectListCreateView.as_view()),
    path('subjects/<int:pk>/', views.SubjectRetrieveUpdateView.as_view()),
    path('topics/', views.TopicListCreateView.as_view()),
    path('topics/<int:pk>/', views.TopicRetrieveUpdateView.as_view()),

    path('internal/enroll-user/', views.EnrollUserAPIView.as_view(), name='internal-enroll-user'),

]