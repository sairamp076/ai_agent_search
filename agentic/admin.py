from django.contrib import admin
from .models import InteractionGraph, SessionRecord, Interaction

@admin.register(SessionRecord)
class SessionRecordAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'created_at')
    search_fields = ('session_key',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('session', 'short_query', 'short_response', 'created_at')
    search_fields = ('user_query', 'ai_response')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def short_query(self, obj):
        return (obj.user_query[:50] + '...') if len(obj.user_query) > 50 else obj.user_query
    short_query.short_description = 'User Query'

    def short_response(self, obj):
        return (obj.ai_response[:50] + '...') if len(obj.ai_response) > 50 else obj.ai_response
    short_response.short_description = 'AI Response'


@admin.register(InteractionGraph)
class InteractionGraphAdmin(admin.ModelAdmin):
    list_display = ('session', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('session__session_key',)
    ordering = ('-created_at',)