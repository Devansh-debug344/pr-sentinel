from abc import ABC, abstractmethod
from typing import Any

from app.agents.contracts import AgentContract, AgentType


class BaseAgent(ABC):
    def __init__(self, agent_type: AgentType, contract: AgentContract):
        self.agent_type = agent_type
        self.contract = contract

    @abstractmethod
    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        pass


__all__ = ["BaseAgent"]
