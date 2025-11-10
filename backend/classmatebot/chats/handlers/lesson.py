from datetime import timezone
from classmatebot.accounts.models import State, Account
from classmatebot.subjects.models import Subject, Enrollment, Bite, Topic, Checkpoint, Milestone
from classmatebot.chats.receivers.receivers import EnrollmentReceiver


class LessonHandler:
    def __init__(self, state: State, user_answer: str):
        self.user_answer = user_answer
        self.state = state
        self.user_phone = state.account.phone_number
        self.context = state.context

    def handle(self):
        if self.user_answer == "/exit-lesson":    
            self.state.state = State.Mode.IDLE
            self.state.context = {}
            self.state.save()
            return "You have exited the lesson."
        
        if self.user_answer != "/next":
            return "Invalid command. Reply /next to continue or /exit-lesson to exit the lesson."

        subject_id = self.context["subject_id"]
        current_topic_index = self.context["current_topic_index"]
        current_bite_index = self.context["current_bite_index"]
        new_topics = self.context["topics"]
        account = Account.objects.get(phone_number=self.user_phone)
        enrollment_receiver = EnrollmentReceiver(to_number=self.user_phone)
        for topic_id in list(new_topics.keys()):
            try:
                Milestone.objects.get(topic_id=topic_id, account=account)
            except Milestone.DoesNotExist:
                newest_topic_id = topic_id
                break

        latest_bites = new_topics[newest_topic_id]             
        for bite in latest_bites:
            try:
                Checkpoint.objects.get(bite_id=bite["bite_id"], account=account)
            except Checkpoint.DoesNotExist:
                newest_bite_id = bite["bite_id"]
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

        message_parts = [f"📚 *Welcome to your lesson for Subject ID {subject_id}!*"]
        message_parts.append(f"\n📝 *Topic {newest_topic_id}*")
        message_parts.append(
            f"\n✨ *Bite {newest_bite_id} - {newest_bite_name} *\n\n"
            f"🔹 {newest_bite_text}\n\n\n"
            f"📊 *Progress*: [{progress_bar}] {completed_bites}/{total_bites} bites completed ({progress_percent}%)\n\n\n"
            f"👉 _Reply '/next' to continue or '/exit-lesson' to stop._"
        )        

        state, _ = State.objects.get_or_create(account=account)
        state.state = State.Mode.IN_LESSON
        state.context = {"subject_id": subject_id, "topics": new_topics, "current_topic_index": newest_topic_id, "current_bite_index": newest_bite_id}    
        state.save()
        Checkpoint.objects.create(bite_id=newest_bite_id, account=account, status=Checkpoint.Status.COMPLETED)
        if newest_bite_id == latest_bites[-1]["bite_id"]:
            Milestone.objects.create(topic_id=newest_topic_id, account=account)
            message_parts.append(f"\n\n\n🎉 Milestone reached!* You've completed Topic {newest_topic_id}! Moving to the next topic...\n")

        if newest_topic_id == list(new_topics.keys())[-1] and newest_bite_id == latest_bites[-1]["bite_id"]:
            message_parts.append("\n\n\n🏆 Congratulations! You've completed all topics and bites in this subject." )
            state.state = State.Mode.IDLE
            state.context = {}
            state.save()    

        return "\n".join(message_parts)
