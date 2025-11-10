from rest_framework import generics, permissions, status

from classmatebot.quizzes.models import Quiz
from classmatebot.quizzes.api.v1.serializers import QuizSerializer, QuizReadSerializer


class QuizListCreateView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return QuizReadSerializer
        return QuizSerializer


class QuizRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return QuizReadSerializer
        return QuizSerializer


