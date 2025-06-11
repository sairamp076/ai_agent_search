# AI Agent Search

A Django-based backend for agentic, AI-powered search and reasoning. This project provides REST APIs for conversational AI, search, and reasoning workflows, leveraging LLMs and web search.

## Features
- Conversational AI with session-based chat history
- Reasoning and step-by-step intermediate results
- Search result integration
- Modular agent architecture
- REST API endpoints for queries, sessions, and interactions

## Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/ai_agent_search.git
   cd ai_agent_search
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```sh
   python manage.py migrate
   ```
4. Start the server:
   ```sh
   python manage.py runserver
   ```

## Usage
- POST `/api/query/` with `{ "query": "your question" }` to interact with the AI agent.
- Manage sessions and view interaction history via the provided endpoints.

## Project Structure
- `agentic/` - Django app with models, views, agents, and utilities
- `ai_agent_search/` - Django project settings and URLs
- `requirements.txt` - Python dependencies
- `setup.py` - Packaging and installation

## License
MIT
