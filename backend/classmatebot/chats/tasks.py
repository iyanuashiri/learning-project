from time import sleep
from celery import shared_task

from wrappers.whastapp import send_whatsapp_message
from classmatebot.subjects.prompts import generate_preference_content
from classmatebot.subjects.models import Subject, Topic
from classmatebot.accounts.models import Account, State
from classmatebot.quizzes.models import Quiz


@shared_task
def generate_preference_content_task(preferences, to_number):
    
    response = generate_preference_content(preferences)
    topic_content = response.topic_content
    topic_name = response.topic_name
    topic_description = response.topic_description
    subject_name = response.subject_name
    subject_description = response.subject_description
    subject = Subject.objects.create_subject_by_user(name=f"{subject_name}", description=subject_description)
    
    topic = Topic.objects.create(name=topic_name, subject=subject, description=topic_description, content=topic_content)
    topic.generate_bites()

    account = Account.objects.get(phone_number=to_number)
    subject.enroll_subject(account=account)

    quiz = Quiz.objects.create(subject=subject, topic=topic, number_of_questions=5, number_of_options=4)
    quiz.generate_questions()

    # sleep(120)  # Simulate some processing time

    send_whatsapp_message(account.phone_number, 
        f"🎉 Your custom course '{subject_name}' has been created based on your preferences!\n\n\n"
        f"*Subject Description*: {subject_description}\n\n"
        f"*Topic*: {topic_name}\n\n"
        f"*Topic Description*: {topic_description}\n\n\n"
        "You have been enrolled in this course. Start learning now!"
    )
    state, _ = State.objects.get_or_create(account=account)
    state.state = State.Mode.IDLE
    state.context = {}
    state.save()    

