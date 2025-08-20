"""
Base Connor Agent

This module defines the base class for all Connor agents, providing common functionality
and interfaces that all agent types will inherit.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from forge.sdk import ForgeLogger

LOG = ForgeLogger(__name__)


class AgentType(Enum):
    """Enumeration of Connor agent types"""
    SRA = "Simple Reflex Agent"
    MBR = "Model-Based Reflex Agent" 
    GAP = "Goal-Based Agent-Planner"
    LA = "Learning Agent"
    UBA = "Utility-Based Agent"
    AA = "Apprentice Agent"


class AgentPhase(Enum):
    """Learning Agent lifecycle phases"""
    CHILD = "child"
    PARENT = "parent"
    GRANDPARENT = "grandparent"
    ARCHIVED = "archived"


@dataclass
class AgentMessage:
    """Standard message format for inter-agent communication"""
    sender_id: str
    sender_type: AgentType
    recipient_id: Optional[str] = None
    recipient_type: Optional[AgentType] = None
    content: Dict[str, Any] = None
    tags: List[str] = None
    priority: int = 1
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.content is None:
            self.content = {}
        if self.tags is None:
            self.tags = []
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


@dataclass
class AgentConfig:
    """Configuration for Connor agents"""
    agent_id: str
    agent_type: AgentType
    phase: Optional[AgentPhase] = None
    family_id: Optional[str] = None
    parent_id: Optional[str] = None
    max_memory_size: int = 1000
    learning_rate: float = 0.01
    enable_logging: bool = True


class BaseConnorAgent(ABC):
    """
    Base class for all Connor agents providing common functionality.
    
    All Connor agents inherit from this class and implement the abstract methods
    to define their specific behavior while sharing common infrastructure.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_id = config.agent_id
        self.agent_type = config.agent_type
        self.memory = []
        self.message_queue = []
        self.active = True
        
        LOG.info(f"Initialized {self.agent_type.value} agent: {self.agent_id}")
    
    @abstractmethod
    async def process_input(self, input_data: Any) -> Any:
        """
        Process input and return output specific to agent type.
        
        Args:
            input_data: The input to process
            
        Returns:
            Processed output
        """
        pass
    
    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle incoming message from another agent.
        
        Args:
            message: Message from another agent
            
        Returns:
            Optional response message
        """
        pass
    
    def add_to_memory(self, item: Any) -> None:
        """Add item to agent memory with size limit."""
        self.memory.append(item)
        if len(self.memory) > self.config.max_memory_size:
            self.memory.pop(0)  # Remove oldest item
    
    def send_message(self, recipient_id: str, recipient_type: AgentType, 
                    content: Dict[str, Any], tags: List[str] = None) -> AgentMessage:
        """Create and return a message to send to another agent."""
        return AgentMessage(
            sender_id=self.agent_id,
            sender_type=self.agent_type,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            content=content,
            tags=tags or []
        )
    
    def receive_message(self, message: AgentMessage) -> None:
        """Receive and queue a message for processing."""
        self.message_queue.append(message)
        LOG.debug(f"Agent {self.agent_id} received message from {message.sender_id}")
    
    async def process_message_queue(self) -> List[AgentMessage]:
        """Process all queued messages and return any responses."""
        responses = []
        while self.message_queue:
            message = self.message_queue.pop(0)
            response = await self.handle_message(message)
            if response:
                responses.append(response)
        return responses
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "active": self.active,
            "memory_size": len(self.memory),
            "queued_messages": len(self.message_queue),
            "phase": self.config.phase.value if self.config.phase else None
        }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type.value})"