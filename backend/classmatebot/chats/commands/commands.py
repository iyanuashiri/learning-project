from abc import ABC, abstractmethod
import threading

from wrappers.whatsapp import send_whatsapp_message
from classmatebot.chats.receivers.receivers import AccountReceiver, SubjectReceiver, EnrollmentReceiver, QuizReceiver
from classmatebot.accounts.models import State
from classmatebot.subjects.models import Topic, Checkpoint, Bite, Milestone
from classmatebot.chats.commands.helpers import trigger_adk_service


class Command(ABC):
    
    @abstractmethod
    def execute(self):
        pass


class HelpCommand(Command):

    def __init__(self, to_number):
        self.to_number = to_number

    def execute(self):
        send_whatsapp_message(self.to_number, """
        👋 *Welcome to ClassmateBot!*

        Here are the available commands to help you get started:

        🆘 */help*  _Get help and see this list of commands._

        👤 */create-account*  _Create a new account to begin your learning journey._

        📚 */get-subjects*  _View all available subjects you can learn._

        ✅ */get-enrolled-subjects*  _See the subjects you are currently enrolled in._

        ➕ */enroll-subject <subject_id>*  _Enroll in a subject using its ID (find the ID in the subjects list)._

        📝 */practice-subject <subject_id>*  _Start a quiz practice for a subject using its ID._

        🎓 */start-lesson <subject_id>*  _Begin a lesson for a subject using its ID._
                              
        🆕 */generate-course <preferences>*  _Create a new subject based on your learning preferences. Prefenrences _
        should include topics of interest, difficulty level, and learning goals._
                              
        *What are preferences?*  
        _Preferences are keywords or phrases that describe what you want to learn. For example:_
            - _"python programming for beginners"_
            - _"history of ancient egypt"_
            - _"basic algebra and equations"_

        _The more specific your preferences, the better we can tailor the course for you!_
                      

        💡 _Tip: Use the subject ID from the subjects list for commands that require it._

        Have fun learning! 🚀          

        """)


class CreateAccountCommand(Command):

    def __init__(self, to_number):
        self.to_number = to_number

    def execute(self):
        account_receiver = AccountReceiver(to_number=self.to_number)
        account, message = account_receiver.create_account()
        return f"{account.phone_number}: {message}"
        
        
class GetSubjectsCommand(Command):

    def __init__(self, to_number):
        self.to_number = to_number

    def execute(self):
        subject_receiver = SubjectReceiver(to_number=self.to_number)
        subjects = subject_receiver.get_subjects()
        if subjects:
            subject_list = "\n".join(
                [f"|  *{subject.name}*  |  `00{subject.id}`  |" for subject in subjects]
            )
            message = (
                "📚 *Available Subjects*\n\n"
                "| Subject Name                | Subject ID |\n"
                "|-----------------------------|------------|\n"
                f"{subject_list}\n\n"
                "Use the Subject ID to enroll, start lessons, or practice quizzes!"

                # [subject.name for subject in subjects]
                
                )
            return message
        else:
            return "No subjects available at the moment."


class EnrollSubjectCommand(Command):
    def __init__(self, to_number, subject_id):
        self.to_number = to_number
        self.subject_id = subject_id

    def execute(self):
        enrollment_receiver = EnrollmentReceiver(to_number=self.to_number)
        enrolled_subject = enrollment_receiver.enroll_subject(subject_id=self.subject_id)
        return f"Successfully enrolled in subject ID: {self.subject_id} - {enrolled_subject.subject.name}"
        

class EnrolledSubjectsCommand(Command):
    def __init__(self, to_number):
        self.to_number = to_number

    def execute(self):
        enrollment_receiver = EnrollmentReceiver(to_number=self.to_number)
        enrollments = enrollment_receiver.enrolled_subjects()
        if enrollments:
            print(enrollments)
            enrolled_list = "\n".join(
                [f"|  *{enrollment['subject__name']}*  |  `00{enrollment['subject__id']}`  |" for enrollment in enrollments]
            )
            message = (
                "📚 *Your Enrolled Subjects*\n\n"
                "| Subject Name                | Subject ID |\n"
                "|-----------------------------|-----------|\n"
                f"{enrolled_list}\n\n"
                "Use the Subject ID for lessons, quizzes, and more!"
                
                )
            return message
        else:
            return "You are not enrolled in any subjects."


class PracticeQuizSubjectCommand(Command):
    def __init__(self, to_number, subject_id):
        self.to_number = to_number
        self.subject_id = subject_id

    def execute(self):
        account_receiver = AccountReceiver(to_number=self.to_number)
        account = account_receiver.get_account()
        if not account:
            return "Account not found. You need an account to practice. Please create an account first using /create-account."
        quiz_receiver = QuizReceiver(to_number=self.to_number)  
        items = quiz_receiver.practice_subject(subject_id=self.subject_id)
        if not items:
            return "No questions available for this subject."
        state, _ = State.objects.get_or_create(account=account)
        state.state = State.Mode.IN_QUIZ
        state.context = {"subject_id": self.subject_id, "questions": items, "current_question_index": 0}    
        state.save()
        question = items[0] if items else None


        total_questions = len(items)        
        current_question_index = 0
        question_text = question["question"]
        
        if question:
            formatted_options = "\n".join([f"  {chr(65+i)}. {opt['option'].lower()}" for i, opt in enumerate(question["options"])])
            
            header = f"🧠 *Question {current_question_index + 1}/{total_questions}*\n\n"
            body = f"{question_text}\n\n*Options:*\n{formatted_options}\n\n"
            footer = "Reply with the option letter (A, B, ...) to answer. To exit, send /exit-quiz." 

            return f"{header}{body}{footer}"
        else:   
            return "No questions available for this subject."


class StartLessonCommand(Command):
    def __init__(self, to_number, subject_id):
        self.to_number = to_number
        self.subject_id = subject_id

    def execute(self):
        account_receiver = AccountReceiver(to_number=self.to_number)
        account = account_receiver.get_account()
        if not account:
            return "Account not found. You need an account to start a lesson. Please create an account first using /create-account."
        enrollment_receiver = EnrollmentReceiver(to_number=self.to_number)
        new_topics = enrollment_receiver.get_content_by_subject(subject_id=self.subject_id)
        
        
        if not new_topics:
            return "You are not enrolled in this subject or no content available."
        
        current_topic_id = None
        current_bite_id = None

        newest_topic_id = None
        newest_bite_id = None
        newest_bite_text = None
        newest_bite_name = None

        for topic_id in list(new_topics.keys()):
            try:
                Milestone.objects.get(topic_id=topic_id, account=account)
            except Milestone.DoesNotExist:
                newest_topic_id = topic_id
                break

        latest_bites = new_topics[newest_topic_id]        
        for bite in latest_bites:
            try:
                Checkpoint.objects.get(bite_id=bite["bite_id"], account=account, status=Checkpoint.Status.COMPLETED)
            except Checkpoint.DoesNotExist:
                newest_bite_id = bite["bite_id"]
                print(newest_bite_id)
                newest_bite_name = bite["bite_name"] if "bite_name" in bite else "Unnamed Bite"
                newest_bite_text = bite["bite_text"] if "bite_text" in bite else "No content available."
                break

        total_bites, completed_bites = enrollment_receiver.get_progress_by_topic(topic_id=newest_topic_id)
        if newest_topic_id is None or newest_bite_id is None:
            return "You've completed all topics and bites in this subject. Great job! 🎉"        
        
        progress_percent = int((completed_bites / total_bites) * 100) if total_bites else 0
        progress_bar_length = 10
        filled_length = int(progress_bar_length * completed_bites // total_bites) if total_bites else 0
        progress_bar = "★" * filled_length + "☆" * (progress_bar_length - filled_length)


        message_parts = [f"📚 *Welcome to your lesson for Subject ID {self.subject_id}!*"]
        message_parts.append(f"\n📝 *Topic {newest_topic_id}*")
        message_parts.append(
            f"\n✨ *Bite {newest_bite_id} - {newest_bite_name} *\n\n"
            f"🔹 {newest_bite_text}\n\n\n"
            f"📊 *Progress*: [{progress_bar}] {completed_bites}/{total_bites} bites completed ({progress_percent}%)\n\n\n"
            f"👉 _Reply '/next' to continue or '/exit-lesson' to stop._")
     
        state, _ = State.objects.get_or_create(account=account)
        state.state = State.Mode.IN_LESSON
        state.context = {"subject_id": self.subject_id, "topics": new_topics, "current_topic_index": newest_topic_id, "current_bite_index": newest_bite_id}    
        state.save()
        Checkpoint.objects.create(bite_id=newest_bite_id, account=account, status=Checkpoint.Status.COMPLETED)
        if current_bite_id == latest_bites[-1]["bite_id"]:
            Milestone.objects.create(topic_id=newest_topic_id, account=account)
            message_parts.append(f"\n\n\n🎉 Milestone reached!* You've completed Topic {current_topic_id}! Moving to the next topic...\n")

        if current_topic_id == list(new_topics.keys())[-1] and current_bite_id == latest_bites[-1]["bite_id"]:
            message_parts.append("\n\n\n🏆 Congratulations! You've completed all topics and bites in this subject." )
            state.state = State.Mode.IDLE
            state.context = {}
            state.save()

        return "\n".join(message_parts)


class GenerateCourseCommand(Command):
    def __init__(self, to_number, preferences):
        self.to_number = to_number
        self.preferences = preferences

    def execute(self):
        account_receiver = AccountReceiver(to_number=self.to_number)
        account = account_receiver.get_account()
        if not account:
            return "Account not found. You need an account to start a lesson. Please create an account first using /create-account."
        
        threading.Thread(
            target=trigger_adk_service,
            args=(self.preferences, self.to_number, account.id)
        ).start()

        subject_receiver = SubjectReceiver(to_number=self.to_number)
        preferences = subject_receiver.create_subject_by_user(preferences=self.preferences)


        state, _ = State.objects.get_or_create(account=account)
        state.state = State.Mode.IN_GENERATION
        state.context = {"preferences": preferences}    
        state.save()
        acknowledgement_message = (
            f"✅ Got it — building your custom course from your preferences:\n\n"
            f"\"_{preferences}_\"\n\n"
            "This usually takes about *2–3 minutes*. I’ll notify you as soon as it’s ready."
        )    

        return acknowledgement_message
