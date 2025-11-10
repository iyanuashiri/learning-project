from django.contrib.admin.apps import AdminConfig


class ClassmateBotAdminConfig(AdminConfig):
    default_site = 'config.admin.ClassmateBotAdminSite'
