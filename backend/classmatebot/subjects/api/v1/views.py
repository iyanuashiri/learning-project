from typing import override

from django.db import IntegrityError

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from config.permissions import IsADKWorker
from classmatebot.subjects.models import Subject, Topic, Enrollment
from classmatebot.accounts.models import Account
from classmatebot.subjects.api.v1.serializers import SubjectSerializer, SubjectReadSerializer, TopicSerializer, TopicReadSerializer, EnrollUserSerializer


class SubjectListCreateView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubjectReadSerializer
        return SubjectSerializer


class SubjectRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectReadSerializer
    permission_classes = (permissions.IsAuthenticated,)


class TopicListCreateView(generics.ListCreateAPIView):
    queryset = Topic.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TopicReadSerializer
        return TopicSerializer


class TopicRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicReadSerializer
    permission_classes = (permissions.IsAuthenticated,)


class EnrollUserAPIView(generics.GenericAPIView):
    """
    Internal endpoint for the ADK worker to enroll a user in a subject.
    """
    serializer_class = EnrollUserSerializer
    permission_classes = [IsADKWorker]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            account = Account.objects.get(id=data['account_id'])
            subject = Subject.objects.get(id=data['subject_id'])
            
            enrollment, created = Enrollment.objects.get_or_create(
                account=account, 
                subject=subject
            )
            
            if created:
                return Response({"status": "enrollment_created"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": "already_enrolled"}, status=status.HTTP_200_OK)
                
        except Account.DoesNotExist:
            return Response({"error": "account_not_found"}, status=status.HTTP_404_NOT_FOUND)
        except Subject.DoesNotExist:
            return Response({"error": "subject_not_found"}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({"error": "database_error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)