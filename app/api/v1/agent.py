from fastapi import APIRouter, Depends

from app.core.auth import Principal, require_scope
from app.core.privacy import require_privacy_consent
from app.core.rate_limit import enforce_rate_limit
from app.schemas.agent import AgentQuestionRequest, AgentQuestionResponse
from app.services.audit import AuditLogger
from app.services.agent.privacy_agent import PrivacyGuardianAgent

router = APIRouter(dependencies=[Depends(enforce_rate_limit), Depends(require_privacy_consent)])
audit_logger = AuditLogger()


@router.post("/ask", response_model=AgentQuestionResponse)
async def ask_agent(
    payload: AgentQuestionRequest,
    principal: Principal = Depends(require_scope("agent:ask")),
) -> AgentQuestionResponse:
    result = await PrivacyGuardianAgent().answer(payload)
    audit_logger.event(
        actor=principal.subject,
        action="agent.ask",
        device_id=payload.device_id,
        summary=f"Agent question answered; evidence_count={len(result.evidence)}",
    )
    return result
