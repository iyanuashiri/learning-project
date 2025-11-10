from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from classmatebot.accounts.constants import Message
from classmatebot.accounts.fields import LowerCaseEmailField
from classmatebot.accounts.managers import AccountManager


# Create your models here.


class Account(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_('first name'), max_length=200, default="")
    last_name = models.CharField(_('last name'), max_length=200, default="")
    phone_number = PhoneNumberField(unique=True, region='NG')
    # email = LowerCaseEmailField(
    #     _('email'),
    #     unique=True,
    #     error_messages={
    #         'unique': Message.NON_UNIQUE_EMAIL.value
    #     }
    # )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    date_updated = models.DateTimeField(_('date updated'), auto_now=True)
    is_active = models.BooleanField(
        _('active status'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into the admin site.'),
    )
    
    objects = AccountManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.fullname

    def clean(self):
        super().clean()

    @property
    def fullname(self):
        return f'{self.first_name} {self.last_name}'
    
    @property
    def total_points(self):
        total = Point.objects.filter(account=self).aggregate(models.Sum('point'))['point__sum']
        return total if total else 0


class State(models.Model):
    class Mode(models.TextChoices):
        IDLE = 'idle', 'Idle'
        IN_QUIZ = 'in_quiz', 'In Quiz'
        IN_LESSON = 'in_lesson', 'In Lesson'
        IN_GENERATION = 'in_generation', 'In Generation'

    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='account_state')
    state = models.CharField(max_length=20, default=Mode.IDLE, choices=Mode.choices)
    context = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('state')
        verbose_name_plural = _('states')

    def __str__(self):
        return f"{self.account.fullname} - {self.state}"    


class PointManager(models.Manager):
    def award_quiz_completed(self, account):
        points = 10  
        point_record = self.create(account=account, event_type='quiz_completed', point=points)
        return point_record
    
    def award_bite_completed(self, account):
        points = 5  
        point_record = self.create(account=account, event_type='bite_completed', point=points)
        return point_record
    
    def award_daily_streak_completed(self, account):
        points = 15  
        point_record = self.create(account=account, event_type='daily_streak_completed', point=points)
        return point_record
    
    def award_milestone_achieved(self, account):
        points = 20  
        point_record = self.create(account=account, event_type='milestone_achieved', point=points)
        return point_record
    
    def award_question_answered_correctly(self, account):
        points = 2  
        point_record = self.create(account=account, event_type='question_answered_correctly', point=points)
        return point_record
    
    def award_question_answered_incorrectly(self, account):
        points = 0  
        point_record = self.create(account=account, event_type='question_answered_incorrectly', point=points)
        return point_record


class Point(models.Model):
    EVENT_TYPE = (
        ('quiz_completed', 'Quiz Completed'),
        ('bite_completed', 'Lesson Completed'),
        ('daily_streak_completed', 'Streak Completed'),
        ('milestone_achieved', 'Milestone Achieved'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_points')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE)
    point = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PointManager()

    class Meta:
        verbose_name = _('point')
        verbose_name_plural = _('points')

    def __str__(self):
        return f"{self.point}"
    
   