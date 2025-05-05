import uuid
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from ..models import SessionRecord
from ..serializers import SessionRecordSerializer

class SessionKeyView(APIView):
    def post(self, request):
        session_key = str(uuid.uuid4())
        session_record = SessionRecord.objects.create(session_key=session_key)
        serializer = SessionRecordSerializer(session_record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def session_keys_list(request):
    tag_filter = request.query_params.get('tags')
    sessions = SessionRecord.objects.all().order_by('-created_at')

    if tag_filter:
        sessions = sessions.filter(interactions__tags__contains=[tag_filter])

    response_data = []
    for session in sessions:
        interactions = session.interactions.order_by('created_at')
        interaction_count = interactions.count()

        title = "🆕 Empty Session — Ready to Chat!" if interaction_count == 0 else \
                interactions.first().user_query if interaction_count == 1 else \
                f"💬 \"{interactions.first().user_query[:40]}{'...' if len(interactions.first().user_query) > 40 else ''}\""

        serializer = SessionRecordSerializer(session)
        session_data = serializer.data
        session_data['title'] = title
        session_data['tags'] = interactions.first().tags if interactions.exists() else []
        response_data.append(session_data)

    return Response(response_data)

class BulkDeleteSessionView(APIView):
    def delete(self, request):
        session_keys = request.data.get('session_keys', [])
        if not isinstance(session_keys, list) or not session_keys:
            return Response({'error': 'session_keys must be a non-empty list.'}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = SessionRecord.objects.filter(session_key__in=session_keys).delete()
        return Response({'message': f'{deleted_count} session records deleted.'}, status=status.HTTP_200_OK)
