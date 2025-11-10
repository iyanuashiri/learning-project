from classmatebot.chats.commands.commands import HelpCommand, CreateAccountCommand, EnrolledSubjectsCommand, EnrollSubjectCommand, GetSubjectsCommand, PracticeQuizSubjectCommand, StartLessonCommand, GenerateCourseCommand


COMMAND_REGISTRY = {
    "/help": {
        "class": HelpCommand,
        "description": "Provides help and lists available commands.",
        "additional_args": [],
        "error_message": "Unknown command. Please type /help for available commands.",
    },
    "/create-account": {
        "class": CreateAccountCommand,
        "description": "Creates a new account for the user.",
        "additional_args": [],
        "error_message": "Failed to create account. Please try again.",
    },
    "/get-subjects": {
        "class": GetSubjectsCommand,
        "description": "Retrieves a list of all subjects.",
        "additional_args": [],
        "error_message": "Failed to retrieve subjects. Please try again.",
    },
    "/get-enrolled-subjects": {
        "class": EnrolledSubjectsCommand,
        "description": "Retrieves a list of subjects the user is enrolled in.",
        "additional_args": [],
        "error_message": "Failed to retrieve enrolled subjects. Please try again.",
    },
    "/enroll-subject": {
        "class": EnrollSubjectCommand,
        "description": "Enrolls the user in a specified subject.",
        "additional_args": ["subject_id"],
        "error_message": "Subject ID is required for enrollment.",
    },
    "/practice-subject": {
        "class": PracticeQuizSubjectCommand,
        "description": "Practices quizzes for a specified subject.",
        "additional_args": ["subject_id"],
        "error_message": "Subject ID is required for practicing.",
    },
    "/start-lesson": {
        "class": StartLessonCommand,
        "description": "Starts a lesson for a specified subject.",
        "additional_args": ["subject_id"],
        "error_message": "Subject ID is required to start a lesson.",
    },
    "/generate-course": {
        "class": GenerateCourseCommand,  
        "description": "Generates a course based on user preferences.",
        "additional_args": ["preferences"],
        "error_message": "Preferences are required to generate a course.",
    }
#     # Add more commands as needed       
   
}