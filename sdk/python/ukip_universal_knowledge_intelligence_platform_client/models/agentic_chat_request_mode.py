from enum import Enum


class AgenticChatRequestMode(str, Enum):
    AUTO = "auto"
    HYBRID = "hybrid"
    NLQ = "nlq"
    RAG = "rag"

    def __str__(self) -> str:
        return str(self.value)
