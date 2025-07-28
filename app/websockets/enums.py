from enum import Enum


class Role(str, Enum):
    user = "user"
    assistant = "assistant"

class AGUIEvent(str, Enum):
    RUN_STARTED = "RUN_STARTED"
    TEXT_MESSAGE_CHUNK = "TEXT_MESSAGE_CHUNK"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    