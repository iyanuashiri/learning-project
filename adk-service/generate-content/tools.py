from typing import Dict, Any, Literal

import httpx
from decouple import config


DJANGO_API_URL = config("DJANGO_API_URL", default="http://127.0.0.1:8000/api/v1")
ADK_WORKER_SECRET = config("ADK_WORKER_SECRET", default="")


auth_headers = {"X-ADK-SECRET": ADK_WORKER_SECRET}
client = httpx.Client(base_url=DJANGO_API_URL, headers=auth_headers)


# --- Tool Definitions ---

def create_subject(subject_name: str, subject_description: str) -> Dict[str, Any]:
    """
    Creates a new subject category in the backend system.

    Use this tool to establish a new high-level subject before adding specific topics to it.
    This is the first step in creating new educational content.

    Args:
        subject_name: The concise name of the subject (e.g., "Astrophysics").
        subject_description: A brief, one-sentence description of the subject.

    Returns:
        A dictionary indicating the outcome.
        On success: {'status': 'success', 'subject': {'id': 1, 'name': 'Astrophysics', ...}}
        On failure: {'status': 'error', 'message': 'Failed to create subject: ...'}
    """
    try:
        response = client.post(
            "/subjects/",
            json={"name": subject_name, "description": subject_description},
        )
        response.raise_for_status()
        return {"status": "success", "subject": response.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to create subject: {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}


def create_topic(subject_id: int, topic_name: str, topic_description: str, topic_content: str) -> Dict[str, Any]:
    """
    Creates a new topic within an existing subject and populates it with content.

    Use this tool after a subject has been created. This function saves the main content
    and triggers the backend to automatically split it into smaller, bite-sized lessons.

    Args:
        subject_id: The integer ID of the parent subject this topic belongs to.
        topic_name: The concise name of the topic (e.g., "The Mystery of Black Holes").
        topic_description: A brief, one-sentence description of the topic.
        topic_content: The full, multi-paragraph text content for the topic.

    Returns:
        A dictionary indicating the outcome.
        On success: {'status': 'success', 'topic': {'id': 1, 'name': 'The Mystery of Black Holes', ...}}
        On failure: {'status': 'error', 'message': 'Failed to create topic: ...'}
    """
    try:
        response = client.post(
            "/topics/",
            json={
                "subject": subject_id,
                "name": topic_name,
                "description": topic_description,
                "content": topic_content
            },
        )
        response.raise_for_status()
        return {"status": "success", "topic": response.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to create topic: {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}


def create_quiz(subject_id: int, topic_id: int, num_questions: int = 5) -> Dict[str, Any]:
    """
    Generates a quiz for a specific topic.

    Use this tool after a topic and its content have been successfully created.
    This triggers the backend to generate a set of multiple-choice questions based on the topic content.

    Args:
        subject_id: The integer ID of the subject.
        topic_id: The integer ID of the topic for which to create a quiz.
        num_questions: The number of questions to generate for the quiz.

    Returns:
        A dictionary indicating the outcome.
        On success: {'status': 'success', 'quiz': {'id': 1, 'topic': 1, ...}}
        On failure: {'status': 'error', 'message': 'Failed to create quiz: ...'}
    """
    try:
        response = client.post(
            "/quizzes/",
            json={
                "subject": subject_id,
                "topic": topic_id,
                "number_of_questions": num_questions,
                "number_of_options": 4
            },
        )
        response.raise_for_status()
        return {"status": "success", "quiz": response.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to create quiz: {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}


def enroll_user(account_id: int, subject_id: int) -> Dict[str, Any]:
    """
    Enrolls a user into a specific subject, giving them access to its content.

    Use this tool after a new subject has been created to grant a user access.

    Args:
        account_id: The integer ID of the user's account.
        subject_id: The integer ID of the subject to enroll the user in.

    Returns:
        A dictionary indicating the outcome.
        On success: {'status': 'success', 'enrollment': {'id': 1, 'account': 1, 'subject': 1}}
        On failure: {'status': 'error', 'message': 'Failed to enroll user: ...'}
    """
    try:
        response = client.post(
            "/internal/enroll-user/",
            json={"account_id": account_id, "subject_id": subject_id},
        )
        response.raise_for_status()
        return {"status": "success", "enrollment": response.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to enroll user: {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}


def notify_user(phone_number: str, message: str) -> Dict[str, Any]:
    """
    Sends a final notification message to the user via WhatsApp.

    Use this tool at the very end of the process to inform the user that their
    new content is ready and they have been enrolled.

    Args:
        phone_number: The user's phone number in international format (e.g., "+14155552671").
        message: The text message to send to the user.

    Returns:
        A dictionary indicating the outcome.
        On success: {'status': 'success', 'detail': 'Message sent successfully.'}
        On failure: {'status': 'error', 'message': 'Failed to notify user: ...'}
    """
    try:
        response = client.post(
            "/internal/notify-user/",
            json={"phone_number": phone_number, "message": message},
        )
        response.raise_for_status()
        return {"status": "success", "detail": response.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to notify user: {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}


def update_user_state(account_id: int, state: Literal['idle', 'in_lesson']) -> Dict[str, Any]:
    """
    Updates the user's state in the backend, typically to reset it to 'idle'.

    Use this tool as the final step to clean up the user's session state after
    the entire content generation and notification process is complete.

    Args:
        account_id: The integer ID of the user's account.
        state: The new state to set for the user. Must be 'idle' or 'in_lesson'.

    Returns:
        A dictionary indicating the outcome.
        On success: {'status': 'success', 'state': {'account': 1, 'state': 'idle', ...}}
        On failure: {'status': 'error', 'message': 'Failed to update state: ...'}
    """
    try:
        response = client.post(
            "/internal/update-user-state/",
            json={"account_id": account_id, "state": state, "context": {}},
        )
        response.raise_for_status()
        return {"status": "success", "state": response.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to update state: {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}