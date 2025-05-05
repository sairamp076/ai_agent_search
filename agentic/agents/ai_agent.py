from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import initialize_agent, AgentType
import os

def create_ai_agent(personality_mode="casual", chat_history=None, temperature=0.5):
    """
    Factory for creating AI agents with personality configurations and tool integrations.
    """
    llm = ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-2.0-flash",
        temperature=temperature
    )

    tools = [TavilySearchResults(max_results=3)]

    prompt_templates = {
        "casual": "You are a friendly and casual AI assistant.",
        "friendly": "You are a friendly AI assistant like a bro.",
        "analytical": "You are a professional and formal AI assistant with analytical skills.",
        "concise": "You are a scholarly and knowledgeable research assistant providing concise answers.",
        "creative": "You are a funny and humorous AI assistant."
    }

    system_prompt = prompt_templates.get(personality_mode, prompt_templates["casual"])

    messages = [
        ("system", f"{system_prompt} Capable of reasoning and using tools. "
                   "Ask clarifying questions when needed."),
    ]
    if chat_history:
        messages.extend(chat_history)

    messages.append(("human", "{input}"))

    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        agent_kwargs={"prompt": messages},
        verbose=False,
        return_intermediate_steps=True,
        handle_parsing_errors=True
    )

    return agent_executor
