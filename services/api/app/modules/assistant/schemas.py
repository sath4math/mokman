from pydantic import BaseModel


class AssistantAskIn(BaseModel):
    question: str


class AssistantAskOut(BaseModel):
    answer: str
