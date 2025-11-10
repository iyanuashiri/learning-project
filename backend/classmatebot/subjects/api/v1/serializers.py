from rest_framework import serializers

from classmatebot.subjects.models import Subject, Topic, Bite


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'description')


class TopicBitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bite
        fields = ('id', 'name', 'bite')


class SubjectTopicsSerializer(serializers.ModelSerializer):
    topic_bites = TopicBitesSerializer(many=True, read_only=True)
    class Meta:
        model = Topic
        fields = ('id', 'name', 'description', 'content', 'topic_bites')


class SubjectReadSerializer(serializers.ModelSerializer):
    subject_topics = SubjectTopicsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Subject
        fields = ('id', 'name', 'description', 'subject_topics')


class TopicSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())

    class Meta:
        model = Topic
        fields = ('id', 'subject', 'name', 'description', 'content')    

    def create(self, validated_data):
        topic = Topic.objects.create(**validated_data)
        topic.generate_bites()
        return topic


class TopicReadSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    topic_bites = TopicBitesSerializer(many=True, read_only=True)
    
    class Meta:
        model = Topic
        fields = ('id', 'subject', 'name', 'description', 'content', 'topic_bites')            


class EnrollUserSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    subject_id = serializers.IntegerField()