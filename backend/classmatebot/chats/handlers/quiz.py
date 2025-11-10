from classmatebot.accounts.models import State, Point
from classmatebot.quizzes.models import Answer, Option, Question


class QuizHandler:
    def __init__(self, state: State, user_answer: str):
        self.state = state
        self.user_answer = user_answer
        self.user_phone = state.account.phone_number
        self.current_question_index = state.context.get("current_question_index", 0)

        self.questions = state.context.get("questions", [])

    def _format_question(self, question_data, index, total_questions):
        question_text = question_data["question"]
        options = question_data["options"]
        formatted_options = "\n".join([f"  {chr(65+i)}. {opt['option'].lower()}" for i, opt in enumerate(options)])

        header = f"🧠 *Question {index}/{total_questions}*\n\n"
        body = f"{question_text}\n\n*Options:*\n{formatted_options}\n\n"
        footer = "Invalid option😡 Reply with the option letter (A, B, ...) to answer. To exit, send /exit-quiz." 

        return f"{header}{body}{footer}"
        
    def handle(self):
        if self.user_answer == "/exit-quiz":    
            self.state.state = State.Mode.IDLE
            self.state.context = {}
            self.state.save()
            return "You have exited the quiz. ✅\nSend /practice-subject <subject_id> to try again."

        
        if self.user_answer.startswith("/"):
            return "You are in a quiz session. Reply with the option letter (e.g. A, B) for the current question, or send /exit-quiz to quit."

        context = self.state.context
        current_question_index = context["current_question_index"]
        questions = context["questions"]
        subject_id = context["subject_id"]

        current_question = questions[current_question_index]
        question = current_question["question"]
        question_id = current_question["question_id"]

        question_instance = Question.objects.get(id=question_id)

        options = current_question["options"] 
        total_questions = len(questions)

        user_choice = self.user_answer.strip().upper()
        valid_letters = [chr(65+i) for i in range(len(options))]  # ['A', 'B', 'C', ...]
        
        if user_choice not in valid_letters:
            formatted_question = self._format_question(current_question, current_question_index + 1, total_questions)
            return formatted_question

        selected_option_index = valid_letters.index(user_choice)
        selected_option_data = options[selected_option_index]
        option_instance = Option.objects.get(id=selected_option_data["option_id"])
        answer = Answer.objects.create(account=self.state.account,
                      question=question_instance, 
                      selected_option=option_instance)
        answer.save()

        if option_instance.is_correct:
            feedback = "✅ Correct! Great job."
            point_record = Point.objects.award_question_answered_correctly(account=self.state.account)
        else:
            correct_opt = next((opt for opt in options if opt.get("is_correct")), None)
            if correct_opt:
                correct_letter = chr(65 + options.index(correct_opt))
                feedback = (
                    f"❌ Not quite.\n"
                    f"Correct answer: {correct_letter}. {correct_opt['option']}"
                )
            else:
                feedback = "❌ Not correct."
            point_record = Point.objects.award_question_answered_incorrectly(account=self.state.account)

        point_line = ""
        if point_record:
            account_total = self.state.account.total_points
            point_line = f"✨ You earned *{point_record.point}* points for this question. Total: *{account_total}* points.\n\n"


        ################################################
        # Move to the next question or finish the quiz
        ###############################################
        self.current_question_index += 1
        if self.current_question_index < total_questions:
            context["current_question_index"] = self.current_question_index
            self.state.context = context
            self.state.save()
            next_question = questions[self.current_question_index]
            next_question_text = next_question["question"]
            next_options = "\n".join([f"  {chr(65+i)}. {opt['option'].lower()}" for i, opt in enumerate(next_question["options"])])
            
            progress_percent = int((self.current_question_index / total_questions) * 100) if total_questions else 0
            progress_bar_length = 10
            filled_length = int(progress_bar_length * self.current_question_index // total_questions) if total_questions else 0
            progress_bar = "★" * filled_length + "☆" * (progress_bar_length - filled_length)
            progress = f"🧾 *Progress*: [{progress_bar}] {self.current_question_index}/{total_questions} answered ({progress_percent}%)\n\n"
            
            next_header = f"➡️ *Next Question ({self.current_question_index+1}/{total_questions})*\n\n"
            next_body = f"{next_question_text}\n\n*Options:*\n{next_options}\n\n"
            next_footer = "Reply with the option letter (A, B, ...). To exit, /exit-quiz."
            
            return f"{feedback}\n\n{point_line}{progress}{next_header}{next_body}{next_footer}"
        else:
            question_ids = [q["question_id"] for q in questions]
            total = Question.objects.filter(id__in=question_ids).count()
            correct_answers_count = Answer.objects.filter(account=self.state.account, 
                                question__id__in=question_ids,
                                selected_option__is_correct=True).count()
            score_percentage = (correct_answers_count / total) * 100 if total > 0 else 0
                    
            completion_point = Point.objects.award_quiz_completed(account=self.state.account)
            completion_line = ""
            if completion_point:
                completion_line = f"\n\n🏆 You earned *{completion_point.point}* points for completing the quiz! Total: *{self.state.account.total_points}* points."

            self.state.state = State.Mode.IDLE
            self.state.context = {}
            self.state.save()

            return (
                f"{feedback}\n\n"
                f"🏁 🎉 *Quiz Complete!* \n"
                f"Score: *{correct_answers_count}/{total}* ({score_percentage}%)\n\n"
                f"Thanks for practicing! Send /practice-subject <subject_id> to try again or /get-subjects to explore other topics. 🎯"
                f"{completion_line}"
            )