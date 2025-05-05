from rest_framework import serializers
from .models import SessionRecord, Interaction

class QueryRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    session_key = serializers.CharField(required=False, allow_blank=True,allow_null=True)
    personality = serializers.CharField(required=False, allow_blank=True,allow_null=True)


class SessionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionRecord
        fields = ['session_key', 'created_at']

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'
