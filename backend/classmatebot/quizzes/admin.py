from django.contrib import admin

from classmatebot.quizzes.models import Quiz, Question, Option
from django.utils.html import format_html

# Register your models here.


class OptionInline(admin.StackedInline):
    model = Option
    fields = ['question', 'option', 'is_correct', 'explanation', 'reason']


class QuestionInline(admin.StackedInline):
    model = Question
    fields = ['quiz', 'question']
    inlines = [OptionInline]


class QuizAdmin(admin.ModelAdmin):
    list_display = ('subject', 'number_of_options')
    inlines = [QuestionInline]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question', 'options')
    inlines = [OptionInline]
    
    def options(self, obj):
        return format_html('<br>'.join([option.option for option in obj.question_options.all()]))

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option)
