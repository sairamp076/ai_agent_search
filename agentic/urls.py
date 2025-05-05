from django.urls import path
from .views.ai_query_views import *
from .views.graph_views import *
from .views.interaction_views import *
from .views.session_views import *

urlpatterns = [
    path('ask/', AIQueryView.as_view(), name='ai_query'),
    path('sessions/<str:session_key>/generate-graph/', generate_interaction_graph, name='generate_interaction_graph'),
    path('sessions/<str:session_key>/graph/', get_interaction_graph, name='get_interaction_graph'),
    path('create-session-key/', SessionKeyView.as_view(), name='create-session-key'),
    path('sessions/', session_keys_list, name='session-keys-list'),
    path('sessions/bulk-delete/', BulkDeleteSessionView.as_view(), name='bulk_delete_sessions'),
    path('summarize-session/<str:session_key>/', summarize_session, name='summarize_session'),
    path('sessions/<str:session_key>/interactions/', interactions_by_session, name='interactions-by-session'),
]
