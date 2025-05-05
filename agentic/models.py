from django.db import models

class SessionRecord(models.Model):
    """
    Stores session-specific metadata such as personality preference and creation timestamp.
    """
    session_key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    personality_mode = models.CharField(
        max_length=50,
        choices=[
            ('casual', 'Casual'),
            ('formal', 'Formal'),
            ('research_assistant', 'Research Assistant'),
            ('comedian', 'Comedian')
        ],
        default='casual',
    )

    def __str__(self):
        return self.session_key


class Interaction(models.Model):
    """
    Logs every user interaction, AI response, reasoning process, and any extracted URLs.
    """
    session = models.ForeignKey(SessionRecord, on_delete=models.CASCADE, related_name='interactions')
    user_query = models.TextField()
    proactive_message = models.TextField(blank=True, null=True)
    ai_response = models.TextField()
    reasoning = models.TextField(blank=True, null=True)
    search_result_urls = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class InteractionGraph(models.Model):
    """
    Represents a knowledge graph generated from AI responses within a session.
    """
    session = models.OneToOneField(SessionRecord, on_delete=models.CASCADE, related_name='graph')
    graph_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
