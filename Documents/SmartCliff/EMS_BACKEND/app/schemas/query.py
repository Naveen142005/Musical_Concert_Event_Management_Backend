from pydantic import BaseModel
from typing import Optional

# User posts a query
class QueryCreate(BaseModel):
    user_id: int
    query_summary: str
    query_priority: str

# Response structure
class QueryResponse(BaseModel):
    query_id: int
    user_id: int
    summary: str
    priority: str
    date: Optional[str]
    status: str
    response: str

# Admin responds
class RespondQueryResponse(BaseModel):
    message: str
    query_id: int
    response: str
    status: str
