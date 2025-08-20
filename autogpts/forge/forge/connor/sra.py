"""
Simple Reflex Agent (SRA)

SRAs are quick responders that act based solely on current input without learning
or planning capabilities. They handle the forefront process as retrievers, 
cataloguers, and messengers.

Functions:
- Retrievers: collect information from database, web, user input, and archive
- Cataloguers: organize new information according to the library system  
- Messengers: relay information between library staff and processes
"""

from typing import Any, Dict, List, Optional
import re
from .base import BaseConnorAgent, AgentMessage, AgentType, AgentConfig
from forge.sdk import ForgeLogger

LOG = ForgeLogger(__name__)


class SimpleReflexAgent(BaseConnorAgent):
    """
    Simple Reflex Agent that provides immediate responses based on current input.
    
    SRAs are the first line of processing in the Connor system, handling input
    classification, tagging, and routing to appropriate agents.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.response_patterns = self._init_response_patterns()
        self.tag_classifiers = self._init_tag_classifiers()
        
    def _init_response_patterns(self) -> Dict[str, str]:
        """Initialize common response patterns for quick responses."""
        return {
            "greeting": r"(?i)\b(hello|hi|hey|greetings)\b",
            "question": r"(?i)\b(what|how|when|where|why|who)\b.*\?",
            "request": r"(?i)\b(please|can you|could you|would you)\b",
            "task": r"(?i)\b(create|write|make|build|generate|produce)\b",
            "search": r"(?i)\b(find|search|lookup|locate|discover)\b",
            "information": r"(?i)\b(tell me|explain|describe|define)\b"
        }
    
    def _init_tag_classifiers(self) -> Dict[str, List[str]]:
        """Initialize classification tags for routing."""
        return {
            "who": ["person", "identity", "individual"],
            "what": ["object", "concept", "definition"],
            "when": ["time", "date", "schedule"],
            "where": ["location", "place", "geography"],
            "why": ["reason", "cause", "explanation"],
            "how": ["process", "method", "procedure"]
        }
    
    async def process_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Process input with immediate reflex responses.
        
        Args:
            input_data: User input or system data to process
            
        Returns:
            Processed data with classification and routing information
        """
        if isinstance(input_data, str):
            text = input_data
        elif isinstance(input_data, dict) and 'text' in input_data:
            text = input_data['text']
        else:
            text = str(input_data)
        
        # Classify input type
        input_type = self._classify_input(text)
        
        # Extract tags
        tags = self._extract_tags(text)
        
        # Determine routing
        routing = self._determine_routing(input_type, tags)
        
        # Create response
        response = {
            "input": text,
            "input_type": input_type,
            "tags": tags,
            "routing": routing,
            "processed_by": self.agent_id,
            "agent_type": self.agent_type.value,
            "quick_response": self._generate_quick_response(input_type, text)
        }
        
        # Add to memory
        self.add_to_memory({
            "input": text,
            "classification": input_type,
            "tags": tags,
            "timestamp": response.get("timestamp")
        })
        
        LOG.info(f"SRA {self.agent_id} processed input: {input_type} with tags: {tags}")
        
        return response
    
    def _classify_input(self, text: str) -> str:
        """Classify the input type based on patterns."""
        for pattern_name, pattern in self.response_patterns.items():
            if re.search(pattern, text):
                return pattern_name
        return "general"
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract classification tags from text."""
        tags = []
        text_lower = text.lower()
        
        # Extract 5W tags (Who, What, When, Where, Why)
        for w_type, keywords in self.tag_classifiers.items():
            if w_type in text_lower:
                tags.append(w_type)
                tags.extend([kw for kw in keywords if kw in text_lower])
        
        # Add domain-specific tags
        if any(word in text_lower for word in ["science", "research", "study"]):
            tags.append("academic")
        if any(word in text_lower for word in ["code", "program", "software"]):
            tags.append("technical")
        if any(word in text_lower for word in ["business", "company", "market"]):
            tags.append("business")
        
        return list(set(tags))  # Remove duplicates
    
    def _determine_routing(self, input_type: str, tags: List[str]) -> Dict[str, str]:
        """Determine which agent types should handle this input."""
        routing = {
            "next_agent": "MBR",  # Default to Model-Based Reflex Agent
            "priority": "normal"
        }
        
        # Route based on input type
        if input_type in ["question", "search", "information"]:
            routing["next_agent"] = "MBR"
            routing["priority"] = "high"
        elif input_type in ["task", "request"]:
            routing["next_agent"] = "GAP"  # Goal-Based Agent-Planner
            routing["priority"] = "high"
        elif "technical" in tags:
            routing["next_agent"] = "LA"  # Learning Agent for complex technical tasks
            routing["priority"] = "normal"
        
        return routing
    
    def _generate_quick_response(self, input_type: str, text: str) -> str:
        """Generate immediate response for user feedback."""
        responses = {
            "greeting": "Hello! I'm processing your request...",
            "question": "I'm analyzing your question and routing it for detailed processing...",
            "request": "I understand your request and am directing it to the appropriate agent...",
            "task": "I'm setting up your task for execution...",
            "search": "I'm initiating a search for the information you requested...",
            "information": "I'm gathering the information you need...",
            "general": "I'm processing your input..."
        }
        
        return responses.get(input_type, responses["general"])
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle messages from other agents.
        
        Args:
            message: Incoming message
            
        Returns:
            Optional response message
        """
        if message.content.get("type") == "feedback":
            # Log feedback from other agents
            feedback = message.content.get("feedback", "")
            LOG.info(f"SRA {self.agent_id} received feedback: {feedback}")
            
            # Update response patterns based on feedback if needed
            # This is a simple learning mechanism for SRAs
            if "success" in feedback.lower():
                self.add_to_memory({"type": "positive_feedback", "content": feedback})
            
            return None
        
        elif message.content.get("type") == "reprocess":
            # Handle reprocessing requests
            original_input = message.content.get("input")
            if original_input:
                result = await self.process_input(original_input)
                return self.send_message(
                    message.sender_id,
                    message.sender_type,
                    {"type": "reprocessed", "result": result}
                )
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics for this SRA."""
        input_types = {}
        tag_frequency = {}
        
        for memory_item in self.memory:
            if isinstance(memory_item, dict):
                # Count input types
                input_type = memory_item.get("classification", "unknown")
                input_types[input_type] = input_types.get(input_type, 0) + 1
                
                # Count tag frequency
                tags = memory_item.get("tags", [])
                for tag in tags:
                    tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
        
        return {
            "total_processed": len(self.memory),
            "input_type_distribution": input_types,
            "tag_frequency": tag_frequency,
            "most_common_type": max(input_types.items(), key=lambda x: x[1])[0] if input_types else None
        }