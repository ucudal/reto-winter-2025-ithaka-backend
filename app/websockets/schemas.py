from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    message: str
    sender: Optional[str] = "user"
    timestamp: Optional[datetime] = None
    type: Optional[str] = "text"
