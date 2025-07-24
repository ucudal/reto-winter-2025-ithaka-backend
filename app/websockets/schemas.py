from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .enums import Role


class UserMessage(BaseModel):
    id: str
    role: Role = Role.assistant
    content: str
    name: Optional[str] = None
    timestamp: Optional[datetime] = None


class AGUIMessage(BaseModel):
    action: str
    payload: UserMessage
    requestId: Optional[str] = None

