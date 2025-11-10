from django.urls import path

from rest_framework.schemas import get_schema_view

from . import views

schema_view = get_schema_view(title='Chats API')

app_name = 'chats'
urlpatterns = [
    path('chats/', views.WhatsAppWebhook.as_view()),

    path('internals/notify-user/', views.NotifyUserAPIView.as_view(), name='internal-notify-user'),
    path('internals/update-user-state/', views.UpdateUserStateAPIView.as_view(), name='internal-update-state'),
]