#flow.py

import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import TypedDict
from langgraph.graph import StateGraph, END
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


def call_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text


class AgentState(TypedDict):
    summary: str
    strategy: str


def summarize_node(state: AgentState):
    summary = state["summary"]
    return {"summary": summary}


def strategy_node(state: AgentState):

    prompt = f"""
    You are an AI supervisor for rural health logistics.

    Outbreak Summary:
    {state['summary']}

    Decide ONE:
    - FULL_RECOMPUTE
    - LOCAL_REALLOCATION
    - MONITOR_ONLY

    Respond strictly in this format:

    DECISION: <option>
    REASON: <short explanation>
    """

    response = call_gemini(prompt)

    return {"strategy": response}

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("summarize", summarize_node)
    graph.add_node("strategy", strategy_node)

    graph.set_entry_point("summarize")

    graph.add_edge("summarize", "strategy")
    graph.add_edge("strategy", END)

    return graph.compile()


agent_graph = build_graph()


def run_agent(summary_text: str):
    initial_state = {
        "summary": summary_text,
        "strategy": ""
    }

    result = agent_graph.invoke(initial_state)

    return result