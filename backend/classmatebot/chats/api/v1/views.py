from rest_framework.decorators import api_view
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.parsers import FormParser, MultiPartParser
from django.db import transaction
from django.utils import timezone

from wrappers.whatsapp import send_whatsapp_message

from config.permissions import IsADKWorker
from classmatebot.accounts.models import Account, State
from classmatebot.chats.api.v1.serializers import WhatsAppMessageSerializer, NotifyUserSerializer, UpdateUserStateSerializer
from classmatebot.chats.commands.registry import COMMAND_REGISTRY
from classmatebot.chats.handlers.quiz import QuizHandler
from classmatebot.chats.handlers.lesson import LessonHandler
from classmatebot.chats.handlers.generation import GenerationHandler


class WhatsAppWebhook(generics.GenericAPIView):
    serializer_class = WhatsAppMessageSerializer
    parser_classes    = [FormParser, MultiPartParser]   
    permission_classes = [permissions.AllowAny]        

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body = serializer.validated_data["Body"].strip()
        user_phone = serializer.validated_data.get("From") 
        user_phone = user_phone.split(":")[1]

        try:
            account = Account.objects.get(phone_number=user_phone)
        except Account.DoesNotExist:
            # account = Account.objects.create(phone_number=user_phone, state=State.INITIAL)
            # account.save()
            send_whatsapp_message(user_phone, "Welcome to ClassmateBot! Type /help for available commands.")
            return Response({"status": "account created"}, status=status.HTTP_201_CREATED)
        
        state = State.objects.get(account=account)
        if state.state == State.Mode.IN_QUIZ:
            quiz_handler = QuizHandler(state, body)
            response_message = quiz_handler.handle()
            if response_message:
                send_whatsapp_message(user_phone, response_message)
            return Response({"status": "quiz response handled"}, status=status.HTTP_200_OK)
        elif state.state == State.Mode.IN_LESSON:
            lesson_handler = LessonHandler(state, body)
            response_message = lesson_handler.handle()
            if response_message:
                send_whatsapp_message(user_phone, response_message)    
            return Response({"status": "lesson response handled"}, status=status.HTTP_200_OK)   

        elif state.state == State.Mode.IN_GENERATION:
            generation_handler = GenerationHandler(state, body)
            response_message = generation_handler.handle()
            if response_message:
                send_whatsapp_message(user_phone, response_message)
            return Response({"status": "generation response handled"}, status=status.HTTP_200_OK)         
        
        command = body.lower().split(" ")[0]

        if command not in COMMAND_REGISTRY.keys():
            send_whatsapp_message(user_phone, "Unknown command. Please type /help for available commands.")
            return Response({"status": "unknown command"}, status=status.HTTP_400_BAD_REQUEST)
        
        command_config = COMMAND_REGISTRY[command]
        command_class = command_config["class"]
        additional_args = command_config.get("additional_args", [])
        error_message = command_config["error_message"]
        
        if additional_args:
            body_parts = body.split(" ")
            if len(body_parts) > len(additional_args):
                kwargs = {arg: body_parts[i + 1] for i, arg in enumerate(additional_args)}
                command_instance = command_class(to_number=user_phone, **kwargs)
            else:
                send_whatsapp_message(user_phone, error_message)
                return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            command_instance = command_class(to_number=user_phone)

        response_message = command_instance.execute()
        if response_message:
            send_whatsapp_message(user_phone, response_message)    
        
        return Response({"status": "help message sent"})


class NotifyUserAPIView(generics.GenericAPIView):
    """
    Internal endpoint for the ADK worker to send a WhatsApp message.
    """
    serializer_class = NotifyUserSerializer
    permission_classes = [IsADKWorker]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            send_whatsapp_message(data['phone_number'], data['message'])
            return Response({"status": "message_sent"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserStateAPIView(generics.GenericAPIView):
    """
    Internal endpoint for the ADK worker to update a user's state.
    """
    serializer_class = UpdateUserStateSerializer
    permission_classes = [IsADKWorker]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            account = Account.objects.get(id=data['account_id'])
            state, _ = State.objects.get_or_create(account=account)
            state.state = data['state']
            state.context = data.get('context', {})
            state.save()
            return Response({"status": "state_updated"}, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({"error": "account_not_found"}, status=status.HTTP_404_NOT_FOUND)