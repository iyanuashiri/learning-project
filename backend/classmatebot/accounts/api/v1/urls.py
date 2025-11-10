from django.urls import path

from rest_framework.schemas import get_schema_view

from . import views

schema_view = get_schema_view(title='Accounts API')

app_name = 'accounts'
urlpatterns = [
    path('auth/users/', views.AccountListCreateView.as_view()),
    path('auth/token/login/', views.TokenCreateAPIView.as_view()),
    path('auth/token/logout/', views.TokenDestroyView.as_view()),
]