from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import SessionRecord, InteractionGraph
from ..agents.ai_agent import create_ai_agent
from .utils.json_utils import clean_json_string
import json

@api_view(['POST'])
def generate_interaction_graph(request, session_key):
    try:
        session = SessionRecord.objects.get(session_key=session_key)
    except SessionRecord.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    interactions = session.interactions.all()
    if not interactions.exists():
        return Response({'error': 'No interactions for this session.'}, status=status.HTTP_400_BAD_REQUEST)

    ai_responses = "\n".join([i.ai_response for i in interactions])
    prompt = (
        "From the following AI responses, extract a knowledge graph in JSON format.\n\n"
        f"{ai_responses}\n\nKnowledge Graph JSON:"
    )
    try:
        agent = create_ai_agent()
        result = agent({"input": prompt})
        graph_json = result.get("output", "{}")
        graph_data = json.loads(clean_json_string(graph_json))
        InteractionGraph.objects.update_or_create(session=session, defaults={'graph_data': graph_data})
        return Response(graph_data)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_interaction_graph(request, session_key):
    try:
        session = SessionRecord.objects.get(session_key=session_key)
        graph = session.graph
    except (SessionRecord.DoesNotExist, InteractionGraph.DoesNotExist):
        return Response({'error': 'Graph not available.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(graph.graph_data)
