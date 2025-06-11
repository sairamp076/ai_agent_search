import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils.crypto import get_random_string
from ..agents.ai_agent import create_ai_agent
from ..models import SessionRecord, Interaction
from ..serializers import QueryRequestSerializer
from .utils.text_parsing import parse_steps

logger = logging.getLogger(__name__)

class AIQueryView(APIView):
    def post(self, request):
        serializer = QueryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data['query']
        session_key = serializer.validated_data.get('session_key')
        personality = serializer.validated_data.get('personality')

        try:
            if not session_key:
                session_key = self.get_or_create_session_key()

            session_record, _ = SessionRecord.objects.get_or_create(session_key=session_key)
            chat_history = self.build_chat_history(session_record)

            agent_executor = create_ai_agent(personality_mode=personality, chat_history=chat_history)
            result = agent_executor.invoke({"input": query + str(chat_history)})

            answer = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            reasoning_points, search_result_urls = parse_steps(intermediate_steps)

            with transaction.atomic():
                Interaction.objects.create(
                    session=session_record,
                    user_query=query,
                    ai_response=answer,
                    reasoning=reasoning_points,
                    search_result_urls=search_result_urls
                )

            response_data = {
                "session_key": session_key,
                "query": query,
                "answer": answer,
                "search_result_urls": search_result_urls,
                "reasoning": reasoning_points
            }

            return Response(response_data)

        except Exception as e:
            logger.error("AIQueryView Error: %s", str(e), exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_or_create_session_key(self):
        session_key = get_random_string(32)
        SessionRecord.objects.create(session_key=session_key)
        return session_key

    def build_chat_history(self, session_record):
        chat_history = []
        for interaction in session_record.interactions.all():
            chat_history.extend([
                ("human", interaction.user_query),
                ("ai", interaction.ai_response)
            ])
        return chat_history


