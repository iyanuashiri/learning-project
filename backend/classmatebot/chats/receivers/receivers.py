from django.db import transaction, IntegrityError

from classmatebot.accounts.models import Account
from classmatebot.subjects.models import Checkpoint, Subject, Enrollment, Topic
from classmatebot.quizzes.models import Quiz
from classmatebot.chats.tasks import generate_preference_content_task


class AccountReceiver:
    def __init__(self, to_number):
        self.to_number = to_number

    def create_account(self):
        try:
            with transaction.atomic():
                account = Account.objects.create(phone_number=self.to_number)
                account.set_unusable_password()  # Set a password if needed
                account.save()
                return account, "Account created successfully."
        except IntegrityError:
            account = Account.objects.get(phone_number=self.to_number)
            return account, "Account already exists."

    def get_account(self):
        try:
            account = Account.objects.get(phone_number=self.to_number)
            return account
        except Account.DoesNotExist:
            return None    
    

class SubjectReceiver:
    def __init__(self, to_number):
        self.to_number = to_number

    def get_subjects(self):
        subjects = Subject.objects.all()
        return subjects
    
    def create_subject_by_user(self, preferences):
        generate_preference_content_task.delay(preferences, self.to_number)
        return preferences


class EnrollmentReceiver:
    def __init__(self, to_number):
        self.to_number = to_number

    def enroll_subject(self, subject_id):
        account = Account.objects.get(phone_number=self.to_number)
        subject = Subject.objects.get(id=subject_id)
        enrollment = Enrollment.objects.create(account=account, subject=subject)    
        return enrollment
    
    def enrolled_subjects(self):
        account = Account.objects.get(phone_number=self.to_number)
        enrollments = Enrollment.objects.get_enrolled_subjects(account=account)
        return enrollments
    
    def get_content_by_subject(self, subject_id):
        account = Account.objects.get(phone_number=self.to_number)
        enrollment = Enrollment.objects.filter(account=account, subject=subject_id).first()
        if not enrollment:
            return None
        subject = enrollment.subject
        topics = subject.subject_topics.all()
        new_topics = {}
        for topic in topics:
            bites = topic.topic_bites.all()
            new_topics[topic.id] = [{"bite_id": bite.id, "bite_name": bite.name, "bite_text": bite.bite} for bite in bites]
        return new_topics
    
    def get_progress_by_topic(self, topic_id):
        account = Account.objects.get(phone_number=self.to_number)
        topic = Topic.objects.get(id=topic_id)
        total_bites = topic.get_total_number_of_bites_by_topic()
        completed_bites = Checkpoint.objects.get_completed_bites_by_topic(account=account, topic=topic)
        return total_bites, completed_bites
    
    
class QuizReceiver:
    def __init__(self, to_number):
        self.to_number = to_number

    def practice_subject(self, subject_id):
        items = Quiz.objects.get_questions_by_subject(subject_id=subject_id)
        return items
       