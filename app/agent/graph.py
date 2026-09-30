import sqlite3

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import tools
from app.config import (
    ALLOWED_MODELS,
    CHECKPOINT_DB_PATH,
    DEFAULT_MODEL,
    MODEL_PROVIDERS,
)


def normalize_model_name(model_name: str | None) -> str:
    """
    Validate selected model from frontend.
    If model is missing or not allowed, fallback to DEFAULT_MODEL.
    """

    if not model_name:
        return DEFAULT_MODEL

    model_name = model_name.strip()

    if model_name not in ALLOWED_MODELS:
        return DEFAULT_MODEL

    return model_name


def build_llm(model_name: str):
    """
    Create the chat model for the provider that serves model_name.
    """

    provider = MODEL_PROVIDERS[model_name]

    if provider == "groq":
        return ChatGroq(
            model=model_name,
            temperature=0.3,
            streaming=True,
            max_retries=1,
            timeout=30,
        )

    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.3,
        streaming=True,
        max_retries=1,
        timeout=30,
    )


def build_agent(model_name: str):
    """
    Build one LangGraph agent for the selected model.
    """

    selected_model = normalize_model_name(model_name)

    llm = build_llm(selected_model)

    llm_with_tools = llm.bind_tools(tools)

    def chatbot_node(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]

        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response]
        }

    tool_node = ToolNode(tools)

    workflow = StateGraph(MessagesState)

    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "chatbot")
    workflow.add_conditional_edges("chatbot", tools_condition)
    workflow.add_edge("tools", "chatbot")

    conn = sqlite3.connect(
        CHECKPOINT_DB_PATH,
        check_same_thread=False
    )

    checkpointer = SqliteSaver(conn)

    return workflow.compile(checkpointer=checkpointer)


_AGENT_CACHE = {}


def get_agent(model_name: str | None = None):
    """
    Return cached LangGraph agent for selected model.
    If not created yet, create it once and reuse it.
    """

    selected_model = normalize_model_name(model_name)

    if selected_model not in _AGENT_CACHE:
        _AGENT_CACHE[selected_model] = build_agent(selected_model)

    return _AGENT_CACHE[selected_model]