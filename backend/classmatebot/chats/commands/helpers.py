import httpx 


ADK_SERVICE_URL = "https://your-adk-service-on-cloud-run.a.run.app/generate-course"


def trigger_adk_service(preferences, phone_number, account_id):
    """
    Sends a non-blocking POST request to the ADK service.
    This replaces the Celery task call.
    """
    try:
        payload = {
            "preferences": preferences,
            "phone_number": phone_number,
            "account_id": account_id
        }
        # We set a short timeout because we don't want to wait
        # for the full response. This is "fire and forget".
        httpx.post(ADK_SERVICE_URL, json=payload, timeout=5.0)
    except httpx.RequestError as e:
        print(f"Failed to trigger ADK service: {e}")
        # You should add logging or error handling here
        # Maybe send a WhatsApp message to the user saying "Failed, please try again"
    except httpx.TimeoutException:
        print("ADK service trigger timed out (which is OK for fire-and-forget)")