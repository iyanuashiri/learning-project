from classmatebot.accounts.models import State


class GenerationHandler:
    def __init__(self, state: State, user_answer: str):
        self.user_answer = user_answer
        self.state = state
        self.user_phone = state.account.phone_number
        self.context = state.context

    def handle(self):
        # Process the request and generate a response
        if self.user_answer == "/exit-generation":
            self.state.state = State.Mode.IDLE
            self.state.context = {}
            self.state.save()
            return "You have exited the generation process."
        
        preferences = self.context["preferences"]

        response = (
                "⏳ Your course is still being generated. This usually takes ~2–3 minutes.\n\n"
                "👉 _Reply '/status' to check progress or /cancel-generation to stop._"
                
            )
        return response