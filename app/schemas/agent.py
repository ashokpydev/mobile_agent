from pydantic import BaseModel

from app.schemas.analysis import MessageAnalysisRequest, UrlAnalysisRequest


class AgentQuestionRequest(BaseModel):
    question: str
    device_id: str | None = None
    message: MessageAnalysisRequest | None = None
    url: UrlAnalysisRequest | None = None


class AgentQuestionResponse(BaseModel):
    answer: str
    actions: list[str]
    confidence: float
    evidence: list[str]

