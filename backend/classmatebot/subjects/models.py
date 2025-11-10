from django.db import models
from django.contrib import admin
from django.utils.html import format_html

from classmatebot.subjects.prompts import generate_bites
from classmatebot.accounts.models import Account
# Create your models here.


class SubjectManager(models.Manager):
    def create_subject_by_user(self, name, description):
        subject = self.create(name=name, description=description, creator_type='user')
        return subject

    def enroll_subject(self, subject, account):
        enrollment = Enrollment.objects.create(subject=subject, account=account)
        return enrollment   
    

class Subject(models.Model):
    CREATOR_TYPE = [
        ('user', 'User'),
        ('admin', 'Admin'),
       
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator_type = models.CharField(max_length=100, choices=CREATOR_TYPE, default='admin')
    date_created = models.DateTimeField(auto_now_add=True)

    objects = SubjectManager()

    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects' 

    def __str__(self):
        return self.name

    @admin.display(description="Topics")
    def get_topics(self):
        return format_html('<br>'.join([topic.name for topic in self.subject_topics.all()]))  

    def enroll_subject(self, account):
        enrollment = Enrollment.objects.create(subject=self, account=account)
        return enrollment   
    

class Topic(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_topics')
    description = models.TextField()
    content = models.TextField()
    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics' 

    def __str__(self):
        return self.name       

    def generate_bites(self):
        response = generate_bites(self.content)
        bites = response.bites
        objs = Bite.objects.bulk_create(
            [Bite(topic=self, bite=bite) for bite in bites]
        )
        return len(bites) 

    def get_total_number_of_bites_by_topic(self):
        return self.topic_bites.count()   

    
class Bite(models.Model):
    name = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='topic_bites')
    bite = models.TextField()
    
    class Meta:
        verbose_name = 'Bite'
        verbose_name_plural = 'Bites' 

    def __str__(self):
        return self.name


class EnrollmentManager(models.Manager):
    def get_enrolled_subjects(self, account):
        return self.filter(account=account).values('subject__name', 'subject__id')


class Enrollment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_enrollments')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_enrollments') 
    date_enrolled = models.DateTimeField(auto_now_add=True) 

    objects = EnrollmentManager()

    class Meta:
        verbose_name = 'enrollment'
        verbose_name_plural = 'enrollments' 
        unique_together = ('subject', 'account')

    def __str__(self):
        return f"{self.account} enrolled in {self.subject.name}"
    

class Milestone(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='topic_milestones')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_milestones')
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'milestone'
        verbose_name_plural = 'milestones' 
        unique_together = ('topic', 'account')

    def __str__(self):
        return f"{self.account} - {self.topic} ({'done' if self.completed else 'in progress'})"

    def get_number_of_bites(self):
        return self.topic.topic_bites.count()    
    

class CheckpointManager(models.Manager):
    def get_completed_bites_by_topic(self, account, topic):
        return self.filter(account=account, bite__topic=topic, status=Checkpoint.Status.COMPLETED).count()  

class Checkpoint(models.Model):
    class Status(models.TextChoices):
        PROGRESSING = 'progressing', 'Progressing'
        COMPLETED = 'completed', 'Completed'
   
    bite = models.ForeignKey(Bite, on_delete=models.CASCADE, related_name='bite_checkpoints')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_checkpoints')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROGRESSING)
    date_completed = models.DateTimeField(auto_now_add=True)

    objects = CheckpointManager()

    class Meta:
        verbose_name = 'checkpoint'
        verbose_name_plural = 'checkpoints' 
        unique_together = ('bite', 'account')

    # def __str__(self):
    #     return f"{self.account} - {self.bite} ({'done' if self.completed else 'in progress'})"
