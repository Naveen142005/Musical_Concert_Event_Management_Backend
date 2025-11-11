from pydantic import BaseModel, Field

class TermsAndConditions(BaseModel):
    id: str = Field(default=None, alias="_id")
    content: str
