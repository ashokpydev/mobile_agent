from typing import Any, TypedDict

from app.schemas.agent import AgentQuestionRequest
from app.services.agent.tools import analyze_message_tool, analyze_url_tool


class AgentState(TypedDict, total=False):
    request: AgentQuestionRequest
    findings: list[str]
    actions: list[str]
    answer: str
    confidence: float


def classify_intent(state: AgentState) -> AgentState:
    request = state["request"]
    findings = state.get("findings", [])
    if request.message:
        findings.append("message_analysis_requested")
    if request.url:
        findings.append("url_analysis_requested")
    return {**state, "findings": findings}


def run_detection_tools(state: AgentState) -> AgentState:
    request = state["request"]
    findings = state.get("findings", [])
    actions = state.get("actions", [])

    if request.message:
        result = analyze_message_tool(request.message)
        findings.append(
            f"Message: {result['classification']} risk={result['risk_score']} confidence={result['confidence']}"
        )
        actions.extend(result["recommended_actions"])

    if request.url:
        result = analyze_url_tool(request.url)
        findings.append(
            f"URL: domain={result['domain']} severity={result['severity']} risk={result['risk_score']}"
        )
        actions.extend(result["recommended_actions"])

    return {**state, "findings": findings, "actions": list(dict.fromkeys(actions))}


def explain(state: AgentState) -> AgentState:
    findings = state.get("findings", [])
    if not findings:
        answer = "Share an app permission list, suspicious message, URL, or sensitive-data sample to analyze."
        confidence = 0.5
    else:
        answer = "I reviewed the supplied artifacts and found: " + "; ".join(findings)
        confidence = 0.82
    return {**state, "answer": answer, "confidence": confidence}


def build_langgraph_workflow() -> Any:
    from langgraph.graph import END, StateGraph

    graph = StateGraph(AgentState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("run_detection_tools", run_detection_tools)
    graph.add_node("explain", explain)
    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "run_detection_tools")
    graph.add_edge("run_detection_tools", "explain")
    graph.add_edge("explain", END)
    return graph.compile()


async def run_agent_workflow(request: AgentQuestionRequest) -> AgentState:
    initial_state: AgentState = {"request": request, "findings": [], "actions": []}
    try:
        workflow = build_langgraph_workflow()
        return await workflow.ainvoke(initial_state)
    except ImportError:
        state = classify_intent(initial_state)
        state = run_detection_tools(state)
        return explain(state)

