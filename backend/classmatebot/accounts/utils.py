from django.contrib.auth import login, logout, user_logged_in, user_logged_out

from rest_framework.authtoken.models import Token


def login_user(request, user):
    token, _ = Token.objects.get_or_create(user=user)
    login(request, user)
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    return token


def logout_user(request):
    Token.objects.filter(user=request.user).delete()
    user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
    logout(request)