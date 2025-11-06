from pydantic import BaseModel


class CancelEventRequest(BaseModel):
    reason: str