import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils.crypto import get_random_string

from .agents.ai_agent import create_ai_agent
from .models import SessionRecord, Interaction

logger = logging.getLogger(__name__)

import re

def parse_steps(steps):
    reasoning_points = []
    urls = []
    url_pattern = re.compile(r'https?://[^\s]+')

    for idx, (action, observation) in enumerate(steps, start=1):
        reasoning_points.append(f"Step {idx}: 🛠️ The agent used **{action.tool}** with input: '{action.tool_input}'.")

        # Try to parse the observation if it's a list of dicts (search result like)
        if isinstance(observation, list) and all(isinstance(item, dict) for item in observation):
            for res_num, result in enumerate(observation, start=1):
                title = result.get("title", "No title")
                url = result.get("url", "No URL")
                content_snippet = result.get("content", "No content")[:200]  # trim long content
                reasoning_points.append(
                    f"  Result {res_num}: 📄 **{title}**\n  🔗 {url}\n  📝 {content_snippet}..."
                )
                urls.append(url)
        else:
            # Fallback for plain text or unstructured observation
            reasoning_points.append(f"Step {idx}: 👀 It observed: {observation}.")

            # Extract URLs if any
            urls.extend(url_pattern.findall(str(observation)))

    return reasoning_points, urls



from rest_framework import serializers

class QueryRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    session_key = serializers.CharField(required=False, allow_blank=True,allow_null=True)
    personality = serializers.CharField(required=False, allow_blank=True,allow_null=True)

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

            agent_executor = create_ai_agent(personality_mode = personality,chat_history=chat_history)
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


# serializers.py
from rest_framework import serializers
from .models import SessionRecord

class SessionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionRecord
        fields = ['session_key', 'created_at']


# views.py
import uuid
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import SessionRecord


class SessionKeyView(APIView):
    def post(self, request, *args, **kwargs):
        # Generate a new session key
        session_key = str(uuid.uuid4())  # UUID generates a unique session key
        session_record = SessionRecord.objects.create(session_key=session_key)

        # Serialize the session record
        serializer = SessionRecordSerializer(session_record)

        return Response(serializer.data, status=status.HTTP_201_CREATED)



from rest_framework import serializers
from .models import SessionRecord, Interaction

class SessionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionRecord
        fields = ['session_key', 'created_at']

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SessionRecord

@api_view(['GET'])
def session_keys_list(request):
    tag_filter = request.query_params.get('tags', None)  # Get 'tags' filter from query parameters
    
    sessions = SessionRecord.objects.all().order_by('-created_at')

    if tag_filter:
        # Filter sessions where at least one interaction has the specified tag(s)
        sessions = sessions.filter(interactions__tags__contains=[tag_filter])

    response_data = []

    for session in sessions:
        interactions = session.interactions.order_by('created_at')
        interaction_count = interactions.count()

        if interaction_count == 0:
            title = "🆕 Empty Session — Ready to Chat!"
        elif interaction_count == 1:
            title = interactions.first().user_query
        else:
            # Auto-summary title if multiple interactions
            title = f"💬 \"{interactions.first().user_query[:40]}{'...' if len(interactions.first().user_query) > 40 else ''}\""

        # Serialize session record
        serializer = SessionRecordSerializer(session)
        session_data = serializer.data

        # Add auto-generated title
        session_data['title'] = title
        if interactions.exists():
            session_data['tags'] = interactions.first().tags

        response_data.append(session_data)

    return Response(response_data)


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Interaction)
def auto_tag_interaction(sender, instance, created, **kwargs):
    if created:
        # Collect the user query and AI response
        conversation = f"User: {instance.user_query}\nAI: {instance.ai_response}"

        # Build the AI prompt to suggest tags based on conversation
        prompt = (
            "Based on the following conversation, suggest relevant tags. "
            "Possible tags include: AI, Coding, History, News, and more.\n\n"
            f"{conversation}\n\nSuggested Tags:"
        )

        try:
            # Use AI agent to generate the tags
            agent = create_ai_agent()
            result = agent({"input": prompt})

            tags = result.get("output", "").split(",")  # Expecting tags to be comma-separated
            tags = [tag.strip() for tag in tags if tag.strip()]  # Clean the tags

            # Save the tags in the interaction
            instance.tags = tags
            instance.save()

        except Exception as e:
            print(f"Error auto-tagging interaction: {e}")


# Get interactions for a specific session key
@api_view(['GET'])
def interactions_by_session(request, session_key):
    try:
        session = SessionRecord.objects.get(session_key=session_key)
    except SessionRecord.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    interactions = session.interactions.all()  # uses related_name='interactions'
    serializer = InteractionSerializer(interactions, many=True)
    return Response(serializer.data)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SessionRecord


@api_view(['GET'])
def summarize_session(request, session_key):
    try:
        session = SessionRecord.objects.get(session_key=session_key)
    except SessionRecord.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    interactions = session.interactions.order_by('created_at')

    if not interactions.exists():
        return Response({'error': 'No interactions to summarize.'}, status=status.HTTP_400_BAD_REQUEST)

    # Collect user queries and AI responses into a conversation string
    conversation = "\n".join([
        f"User: {interaction.user_query}\nAI: {interaction.ai_response}"
        for interaction in interactions
    ])

    # Build AI prompt for bullet point summary
    prompt = (
        "You are a helpful assistant. Based on the following conversation between a user and an AI agent, "
        "generate a concise summary of the key points and topics discussed during the session. "
        "Format the summary as multiple clear bullet points.\n\n"
        f"{conversation}\n\nSummary (as bullet points):"
    )

    try:
        # Use AI agent to generate bullet point conversation summary
        agent = create_ai_agent()
        result = agent({"input": prompt})

        summary = result.get("output", "No summary available.")
        
        # Split the output into an array of bullet points
        bullet_points = [point.strip() for point in summary.split("\n") if point.strip()]

        return Response({
            "session_key": session_key,
            "conversation_summary": bullet_points
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SessionRecord

class BulkDeleteSessionView(APIView):
    def delete(self, request, *args, **kwargs):
        session_keys = request.data.get('session_keys', [])
        if not isinstance(session_keys, list) or not session_keys:
            return Response(
                {'error': 'session_keys must be a non-empty list.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = SessionRecord.objects.filter(session_key__in=session_keys).delete()
        
        return Response(
            {'message': f'{deleted_count} session records deleted.'},
            status=status.HTTP_200_OK
        )


from rest_framework.decorators import api_view
from .models import Interaction, SessionRecord, InteractionGraph
from rest_framework.response import Response
from rest_framework import status
from .agents.ai_agent import create_ai_agent

@api_view(['POST'])
def generate_interaction_graph(request, session_key):
    try:
        session = SessionRecord.objects.get(session_key=session_key)
    except SessionRecord.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    interactions = session.interactions.all()
    if not interactions.exists():
        return Response({'error': 'No interactions for this session.'}, status=status.HTTP_400_BAD_REQUEST)

    # Only use AI responses for graph generation
    ai_responses = "\n".join([i.ai_response for i in interactions])

    # Prompt for extracting a knowledge graph from AI responses only
    prompt = (
        "From the following AI responses, extract a knowledge graph in JSON format. "
        "Each concept or entity should be a node with 'id', 'label' (e.g., 'Concept', 'Entity'), and 'content'. "
        "Create edges based on logical, semantic, or causal relationships between concepts, with 'source', 'target', and 'relation'. "
        "Example:\n"
        "{"
        "  'nodes': ["
        "    {'id': 'n1', 'label': 'Concept', 'content': 'Machine Learning'},"
        "    {'id': 'n2', 'label': 'Concept', 'content': 'Supervised Learning'}"
        "  ],"
        "  'edges': ["
        "    {'source': 'n2', 'target': 'n1', 'relation': 'is_a_type_of'}"
        "  ]"
        "}\n\n"
        f"AI Responses:\n{ai_responses}\n\n"
        "Knowledge Graph JSON:"
    )

    try:
        agent = create_ai_agent()
        result = agent({"input": prompt})
        graph_json = result.get("output", "{}")

        import json
        graph_data = clean_json_string(graph_json)
        graph_data = json.loads(graph_data)

        InteractionGraph.objects.update_or_create(
            session=session,
            defaults={'graph_data': graph_data}
        )

        return Response(graph_data)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_interaction_graph(request, session_key):
    try:
        session = SessionRecord.objects.get(session_key=session_key)
        graph = session.graph
    except SessionRecord.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except InteractionGraph.DoesNotExist:
        return Response({'error': 'Graph not generated yet for this session.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(graph.graph_data)


import re
import json

def clean_json_string(json_str):
    # Remove markdown-style ```json ... ``` wrappers
    cleaned = re.sub(r"^```json\s*|\s*```$", "", json_str.strip(), flags=re.DOTALL)
    return cleaned
