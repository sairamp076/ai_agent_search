# Architecture Overview

## High-Level Design

- **Django REST Framework** is used to expose API endpoints for AI queries, session management, and interaction history.
- **Agentic Layer**: The `agents/ai_agent.py` module defines the logic for invoking LLMs and handling reasoning steps.
- **Session & Interaction Models**: `SessionRecord` and `Interaction` models track user sessions and chat history.
- **Views**: API endpoints in `views/` handle requests, build chat history, invoke agents, and return structured responses.
- **Utilities**: Parsing and processing of intermediate reasoning steps is handled in `views/utils/text_parsing.py`.

## Data Flow

1. **User Query**: Client sends a query to the `/api/query/` endpoint.
2. **Session Handling**: The backend checks or creates a session, retrieves chat history.
3. **Agent Execution**: The AI agent is invoked with the query and chat history.
4. **Reasoning & Search**: The agent may perform reasoning and web search, returning intermediate steps.
5. **Persistence**: The query, response, reasoning, and URLs are saved as an `Interaction`.
6. **Response**: The API returns the answer, reasoning, and search results to the client.

## Key Files
- `agentic/views/ai_query_views.py`: Main API logic for handling queries.
- `agentic/agents/ai_agent.py`: Agent logic and LLM integration.
- `agentic/models.py`: Django models for sessions and interactions.
- `agentic/serializers.py`: DRF serializers for request/response validation.
- `agentic/views/utils/text_parsing.py`: Utilities for parsing agent steps.

## Extensibility
- Add new agent types in `agents/`
- Extend API endpoints in `views/`
- Add new fields to models for richer interaction tracking

---
For more details, see the code and comments in each module.
