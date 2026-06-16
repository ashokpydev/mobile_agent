from app.schemas.agent import AgentQuestionRequest, AgentQuestionResponse
from app.services.agent.workflow import run_agent_workflow


class PrivacyGuardianAgent:
    """LangGraph-ready orchestration layer for privacy and security Q&A."""

    async def answer(self, payload: AgentQuestionRequest) -> AgentQuestionResponse:
        state = await run_agent_workflow(payload)
        return AgentQuestionResponse(
            answer=state["answer"],
            actions=state.get("actions", ["Run a targeted privacy scan."]),
            confidence=state["confidence"],
            evidence=state.get("findings", []),
        )
