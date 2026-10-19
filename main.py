import os
from typing import TypedDict, Annotated
import operator
# Inside the Langraph we will need to create states, so this packages will be
# used to create those states or in other language the shared memoryview

import psycopg
from langgraph.graph import StateGraph, START, END
# In LangGraph we will need to create states this is for that purpose

from langgraph.checkpoint.postgres import PostgresSaver
# The postgres that stores the long term memory is needed to be saved
# somewhere and connected with the database, this is that database

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
# System messages are the system [prompt], ai agents reply is ai message,any message,
# can keep any kind of message

from langchain_groq import ChatGroq
# we need to connect the groq with our tool


from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from guardrails import (
    SYSTEM_RULES,
    budget_instruction,
    sanitize_tool_output,
    redact_secrets,
    validate_query,
)
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b"
)

# State
class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    original_query: str
    follow_up: str
    previous_plan: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int

# Flight Agent
def flight_agent(state: TravelState):
    query = state["user_query"]
    # Tool output is untrusted: strip injection-like lines before the LLM sees it
    flight_data = sanitize_tool_output(search_flights(query))
    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight results fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# Hotel Agent
def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    hotel_results = sanitize_tool_output(tavily_search(query))

    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# Itinerary Agent
def itinerary_agent(state: TravelState):
    is_revision = bool(state.get("follow_up"))
    planning_request = state.get("original_query") or state["user_query"]
    if is_revision:
        planning_request += f" {state['follow_up']}"

    prompt = f"""
    {"Revise the existing travel itinerary to incorporate the user's latest requested changes. Return a complete updated itinerary, not just a summary or acknowledgement." if is_revision else "Create a travel itinerary."}
    Original Travel Request:
    {state.get('original_query') or state['user_query']}

    Latest User Request:
    {state.get('follow_up') or "No follow-up; create the initial plan."}

    Previous Plan:
    {state.get('previous_plan') or "No previous plan; this is the initial request."}

    {budget_instruction(planning_request)}

    <data>
    Flight Results:
    {state['flight_results']}
    </data>

    <data>
    Hotel Results:
    {state['hotel_results']}
    </data>
    """

    response = llm.invoke([
        SystemMessage(content=SYSTEM_RULES),
        HumanMessage(content=prompt)
    ])
    response.content = redact_secrets(response.content)

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# Final Response Agent
def final_agent(state: TravelState):
    is_revision = bool(state.get("follow_up"))
    planning_request = state.get("original_query") or state["user_query"]
    if is_revision:
        planning_request += f" {state['follow_up']}"

    final_prompt = f"""
    {"This is a plan revision. Start your answer with the exact heading 'Here is your revised travel plan'. Then provide the complete revised plan, incorporating every latest requested change. Do not merely acknowledge the request, summarize changes, or tell the user what you would do. Recalculate and show a realistic cost breakdown and total when a budget is given; make the itinerary and recommendations fit the new constraints. Ensure the stated total matches the itemized costs. If a constraint cannot be met, explain why and provide the closest feasible alternative." if is_revision else "Generate the complete initial travel plan for this request."}

    Original Travel Request:
    {state.get('original_query') or state['user_query']}

    Latest User Request:
    {state.get('follow_up') or "No follow-up; create the initial plan."}

    Previous Plan (revise this rather than starting from scratch):
    {state.get('previous_plan') or "No previous plan; this is the initial request."}

    {budget_instruction(planning_request)}

    <data>
    Flights:
    {state['flight_results']}
    </data>

    <data>
    Hotels:
    {state['hotel_results']}
    </data>

    <data>
    Itinerary:
    {state['itinerary']}
    </data>
    """

    response = llm.invoke([
        SystemMessage(content=SYSTEM_RULES),
        HumanMessage(content=final_prompt)
    ])
    response.content = redact_secrets(response.content)
    if is_revision and not response.content.lstrip().lower().startswith(
        "here is your revised travel plan"
    ):
        response.content = f"Here is your revised travel plan\n\n{response.content}"

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


# Persistent connection so both CLI and Streamlit can share the compiled app
_conn = psycopg.connect(DATABASE_URL, autocommit=True)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()

app = graph.compile(checkpointer=checkpointer)
stateless_app = graph.compile()


if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "user_aarohi"
        }
    }

    user_input = input("Enter travel request: ")

    ok, user_input = validate_query(user_input)
    if not ok:
        raise SystemExit(user_input)

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "original_query": user_input,
            "follow_up": "",
            "previous_plan": "",
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    print("\nFINAL RESPONSE:\n")

    for msg in result["messages"]:
        print(msg.content)