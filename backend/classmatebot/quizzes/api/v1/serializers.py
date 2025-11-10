from rest_framework import serializers

from classmatebot.quizzes.models import Quiz, Question, Option
from classmatebot.subjects.api.v1.serializers import SubjectSerializer, TopicSerializer
from classmatebot.subjects.models import Subject, Topic


class QuizSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())
    
    class Meta:
        model = Quiz
        fields = ('id', 'subject', 'topic', 'number_of_questions', 'number_of_options')

    def create(self, validated_data):
        quiz = Quiz.objects.create(**validated_data)
        quiz.generate_questions()
        return quiz


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'question', 'option', 'is_correct', 'explanation', 'reason')


class QuestionSerializer(serializers.ModelSerializer):
    question_options = OptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ('id', 'quiz', 'question', 'question_options')


class QuizReadSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    quiz_questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ('id', 'subject', 'topic', 'number_of_questions', 'number_of_options', 'quiz_questions')
