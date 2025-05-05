from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import SessionRecord
from ..serializers import InteractionSerializer
from ..agents.ai_agent import create_ai_agent

@api_view(['GET'])
def interactions_by_session(request, session_key):
    try:
        session = SessionRecord.objects.get(session_key=session_key)
    except SessionRecord.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    interactions = session.interactions.all()
    serializer = InteractionSerializer(interactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def summarize_session(request, session_key):
    try:
        session = SessionRecord.objects.get(session_key=session_key)
    except SessionRecord.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    interactions = session.interactions.order_by('created_at')
    if not interactions.exists():
        return Response({'error': 'No interactions to summarize.'}, status=status.HTTP_400_BAD_REQUEST)

    conversation = "\n".join([f"User: {i.user_query}\nAI: {i.ai_response}" for i in interactions])
    prompt = (
        "You are a helpful assistant. Based on the following conversation between a user and an AI agent, "
        "generate a concise summary of the key points as bullet points.\n\n"
        f"{conversation}\n\nSummary:"
    )
    try:
        agent = create_ai_agent()
        result = agent({"input": prompt})
        bullet_points = [point.strip() for point in result.get("output", "").split("\n") if point.strip()]
        return Response({"session_key": session_key, "conversation_summary": bullet_points})

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
