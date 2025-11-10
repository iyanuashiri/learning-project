from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework import views

from classmatebot.accounts.models import Account
from classmatebot.accounts.api.v1.serializers import AccountSerializer, AccountCreateSerializer, TokenCreateSerializer
from classmatebot.accounts.utils import login_user, logout_user


class AccountListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "GET":
            return AccountSerializer
        return AccountCreateSerializer


class TokenCreateAPIView(generics.GenericAPIView):
    """
    Use this endpoint to obtain user authentication token.
    """
    serializer_class = TokenCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        token = login_user(request=request, user=user)
        data = {
            'auth_token': token.key,
            'phone_number': str(user.phone_number),
        }
        return Response(data=data, status=status.HTTP_200_OK)


class TokenDestroyView(views.APIView):
    """
    Use this endpoint to logout user (remove user authentication token).
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


