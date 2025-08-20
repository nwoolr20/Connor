"""
Model-Based Reflex Agent (MBR)

MBRs maintain an internal model of the world, allowing them to make informed
decisions based on context beyond just the current input. They use their
internal model to provide contextually appropriate responses.
"""

from typing import Any, Dict, List, Optional, Tuple
import json
from .base import BaseConnorAgent, AgentMessage, AgentType, AgentConfig
from forge.sdk import ForgeLogger

LOG = ForgeLogger(__name__)


class WorldModel:
    """Internal world model for MBR agents."""
    
    def __init__(self):
        self.entities = {}  # Known entities and their properties
        self.relationships = {}  # Relationships between entities
        self.contexts = {}  # Contextual information
        self.patterns = {}  # Observed patterns
        
    def add_entity(self, entity_id: str, properties: Dict[str, Any]) -> None:
        """Add or update an entity in the world model."""
        self.entities[entity_id] = properties
        
    def add_relationship(self, entity1: str, entity2: str, relationship: str) -> None:
        """Add a relationship between two entities."""
        if entity1 not in self.relationships:
            self.relationships[entity1] = {}
        self.relationships[entity1][entity2] = relationship
        
    def get_context(self, query: str) -> Dict[str, Any]:
        """Get relevant context for a query."""
        context = {
            "relevant_entities": [],
            "relevant_relationships": [],
            "patterns": []
        }
        
        # Simple keyword matching for context retrieval
        query_lower = query.lower()
        
        # Find relevant entities
        for entity_id, properties in self.entities.items():
            entity_text = json.dumps(properties).lower()
            if any(word in entity_text for word in query_lower.split()):
                context["relevant_entities"].append({
                    "id": entity_id,
                    "properties": properties
                })
        
        # Find relevant relationships
        for entity1, relationships in self.relationships.items():
            if entity1.lower() in query_lower:
                for entity2, relationship in relationships.items():
                    context["relevant_relationships"].append({
                        "from": entity1,
                        "to": entity2,
                        "relationship": relationship
                    })
        
        return context
    
    def update_pattern(self, pattern_id: str, pattern_data: Dict[str, Any]) -> None:
        """Update observed patterns."""
        self.patterns[pattern_id] = pattern_data


class ModelBasedReflexAgent(BaseConnorAgent):
    """
    Model-Based Reflex Agent that uses an internal world model for context-aware processing.
    
    MBRs receive processed input from SRAs and use their world model to provide
    more informed responses before routing to GAPs.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.world_model = WorldModel()
        self.decision_history = []
        self.context_cache = {}
        
        # Initialize with some basic world knowledge
        self._initialize_world_model()
        
    def _initialize_world_model(self) -> None:
        """Initialize the world model with basic knowledge."""
        # Add basic entities
        self.world_model.add_entity("user", {
            "type": "human",
            "role": "information_seeker",
            "capabilities": ["ask_questions", "provide_feedback", "make_requests"]
        })
        
        self.world_model.add_entity("system", {
            "type": "ai_system",
            "role": "information_provider",
            "capabilities": ["process_information", "generate_responses", "learn"]
        })
        
        # Add basic relationships
        self.world_model.add_relationship("user", "system", "interacts_with")
        self.world_model.add_relationship("system", "user", "serves")
        
        # Add basic patterns
        self.world_model.update_pattern("question_answering", {
            "trigger": "question",
            "process": "analyze -> retrieve -> synthesize -> respond",
            "success_indicators": ["user_satisfaction", "accuracy", "completeness"]
        })
        
    async def process_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Process input using the internal world model for context.
        
        Args:
            input_data: Processed data from SRA or direct input
            
        Returns:
            Enhanced response with contextual information
        """
        # Extract input information
        if isinstance(input_data, dict):
            text = input_data.get("input", "")
            tags = input_data.get("tags", [])
            input_type = input_data.get("input_type", "general")
            routing = input_data.get("routing", {})
        else:
            text = str(input_data)
            tags = []
            input_type = "general"
            routing = {}
        
        # Get context from world model
        context = self.world_model.get_context(text)
        
        # Analyze input with context
        analysis = self._analyze_with_context(text, tags, input_type, context)
        
        # Make informed decision
        decision = self._make_informed_decision(analysis, context)
        
        # Update world model with new information
        self._update_world_model(text, analysis, decision)
        
        # Create enhanced response
        response = {
            "original_input": text,
            "tags": tags,
            "input_type": input_type,
            "context": context,
            "analysis": analysis,
            "decision": decision,
            "processed_by": self.agent_id,
            "agent_type": self.agent_type.value,
            "next_steps": self._determine_next_steps(decision),
            "confidence": decision.get("confidence", 0.5)
        }
        
        # Store decision in history
        self.decision_history.append({
            "input": text,
            "analysis": analysis,
            "decision": decision,
            "timestamp": response.get("timestamp")
        })
        
        # Add to memory
        self.add_to_memory(response)
        
        LOG.info(f"MBR {self.agent_id} processed input with confidence: {response['confidence']:.2f}")
        
        return response
    
    def _analyze_with_context(self, text: str, tags: List[str], 
                            input_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze input using contextual information."""
        analysis = {
            "complexity": self._assess_complexity(text, tags),
            "domain": self._identify_domain(text, tags, context),
            "intent": self._determine_intent(text, input_type, context),
            "entities_mentioned": self._extract_entities(text, context),
            "required_knowledge": self._identify_required_knowledge(text, context)
        }
        
        return analysis
    
    def _assess_complexity(self, text: str, tags: List[str]) -> str:
        """Assess the complexity of the input."""
        complexity_indicators = {
            "low": ["simple", "basic", "easy", "quick"],
            "medium": ["analyze", "compare", "explain", "describe"],
            "high": ["complex", "detailed", "comprehensive", "intricate"]
        }
        
        text_lower = text.lower()
        complexity_scores = {"low": 0, "medium": 0, "high": 0}
        
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            complexity_scores[level] = score
        
        # Factor in number of tags as complexity indicator
        if len(tags) > 5:
            complexity_scores["high"] += 1
        elif len(tags) > 2:
            complexity_scores["medium"] += 1
        else:
            complexity_scores["low"] += 1
        
        return max(complexity_scores.items(), key=lambda x: x[1])[0]
    
    def _identify_domain(self, text: str, tags: List[str], 
                        context: Dict[str, Any]) -> str:
        """Identify the domain of the input."""
        domain_keywords = {
            "technology": ["software", "code", "programming", "computer", "AI"],
            "science": ["research", "study", "experiment", "hypothesis", "data"],
            "business": ["market", "company", "profit", "strategy", "management"],
            "education": ["learn", "teach", "student", "school", "knowledge"],
            "general": []
        }
        
        text_lower = text.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain
        
        # Check tags for domain indicators
        for tag in tags:
            for domain, keywords in domain_keywords.items():
                if tag.lower() in keywords:
                    return domain
        
        return "general"
    
    def _determine_intent(self, text: str, input_type: str, 
                         context: Dict[str, Any]) -> str:
        """Determine the user's intent."""
        intent_mapping = {
            "question": "information_seeking",
            "request": "task_execution",
            "task": "goal_achievement",
            "search": "information_retrieval",
            "greeting": "social_interaction"
        }
        
        return intent_mapping.get(input_type, "general_interaction")
    
    def _extract_entities(self, text: str, context: Dict[str, Any]) -> List[str]:
        """Extract entities mentioned in the text."""
        entities = []
        
        # Check against known entities in world model
        for entity_id in self.world_model.entities.keys():
            if entity_id.lower() in text.lower():
                entities.append(entity_id)
        
        # Look for entities in context
        for entity in context.get("relevant_entities", []):
            if entity["id"] not in entities:
                entities.append(entity["id"])
        
        return entities
    
    def _identify_required_knowledge(self, text: str, context: Dict[str, Any]) -> List[str]:
        """Identify what knowledge is required to handle the input."""
        knowledge_areas = []
        
        # Based on patterns in world model
        for pattern_id, pattern_data in self.world_model.patterns.items():
            trigger = pattern_data.get("trigger", "")
            if trigger.lower() in text.lower():
                knowledge_areas.append(pattern_id)
        
        # Based on domain
        domain_knowledge = {
            "technology": ["programming_concepts", "software_engineering", "AI_ML"],
            "science": ["research_methods", "scientific_principles", "data_analysis"],
            "business": ["business_strategy", "market_analysis", "management"],
            "education": ["pedagogy", "curriculum", "learning_theory"]
        }
        
        domain = self._identify_domain(text, [], context)
        if domain in domain_knowledge:
            knowledge_areas.extend(domain_knowledge[domain])
        
        return list(set(knowledge_areas))
    
    def _make_informed_decision(self, analysis: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Make an informed decision based on analysis and context."""
        decision = {
            "action": "process_and_route",
            "confidence": 0.5,
            "reasoning": [],
            "recommended_agent": "GAP",  # Default to Goal-Based Agent-Planner
            "processing_strategy": "standard"
        }
        
        # Adjust confidence based on context availability
        if context["relevant_entities"]:
            decision["confidence"] += 0.2
        if context["relevant_relationships"]:
            decision["confidence"] += 0.1
        if context["patterns"]:
            decision["confidence"] += 0.1
        
        # Adjust based on complexity
        complexity = analysis.get("complexity", "medium")
        if complexity == "low":
            decision["confidence"] += 0.1
            decision["processing_strategy"] = "fast_track"
        elif complexity == "high":
            decision["confidence"] -= 0.1
            decision["recommended_agent"] = "LA"  # Learning Agent for complex tasks
            decision["processing_strategy"] = "deep_analysis"
        
        # Adjust based on intent
        intent = analysis.get("intent", "general_interaction")
        if intent == "information_seeking":
            decision["action"] = "retrieve_and_synthesize"
            decision["recommended_agent"] = "UBA"  # Utility-Based Agent for optimization
        elif intent == "task_execution":
            decision["action"] = "plan_and_execute"
            decision["recommended_agent"] = "GAP"
        elif intent == "goal_achievement":
            decision["action"] = "strategic_planning"
            decision["recommended_agent"] = "GAP"
        
        # Cap confidence at 1.0
        decision["confidence"] = min(decision["confidence"], 1.0)
        
        # Add reasoning
        decision["reasoning"] = [
            f"Complexity assessed as {complexity}",
            f"Intent identified as {intent}",
            f"Domain: {analysis.get('domain', 'general')}",
            f"Context entities: {len(context.get('relevant_entities', []))}",
            f"Recommended agent: {decision['recommended_agent']}"
        ]
        
        return decision
    
    def _determine_next_steps(self, decision: Dict[str, Any]) -> List[str]:
        """Determine the next steps based on the decision."""
        next_steps = []
        
        action = decision.get("action", "process_and_route")
        recommended_agent = decision.get("recommended_agent", "GAP")
        
        if action == "retrieve_and_synthesize":
            next_steps = [
                "Route to information retrieval system",
                f"Engage {recommended_agent} for processing",
                "Synthesize results",
                "Prepare user response"
            ]
        elif action == "plan_and_execute":
            next_steps = [
                f"Route to {recommended_agent}",
                "Create execution plan",
                "Monitor progress",
                "Provide status updates"
            ]
        elif action == "strategic_planning":
            next_steps = [
                f"Route to {recommended_agent}",
                "Analyze goals and constraints",
                "Develop strategy",
                "Execute plan"
            ]
        else:
            next_steps = [
                f"Route to {recommended_agent}",
                "Process request",
                "Generate response"
            ]
        
        return next_steps
    
    def _update_world_model(self, text: str, analysis: Dict[str, Any], 
                          decision: Dict[str, Any]) -> None:
        """Update the world model with new information."""
        # Add new entities if discovered
        entities = analysis.get("entities_mentioned", [])
        for entity in entities:
            if entity not in self.world_model.entities:
                self.world_model.add_entity(entity, {
                    "type": "discovered_entity",
                    "first_mention": text,
                    "context": analysis.get("domain", "general")
                })
        
        # Update patterns based on successful decisions
        if decision.get("confidence", 0) > 0.7:
            pattern_id = f"{analysis.get('intent', 'general')}_{analysis.get('domain', 'general')}"
            self.world_model.update_pattern(pattern_id, {
                "trigger": analysis.get("intent", "general"),
                "domain": analysis.get("domain", "general"),
                "successful_action": decision.get("action", ""),
                "confidence": decision.get("confidence", 0)
            })
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle messages from other agents."""
        if message.content.get("type") == "context_request":
            # Provide context for another agent
            query = message.content.get("query", "")
            context = self.world_model.get_context(query)
            
            return self.send_message(
                message.sender_id,
                message.sender_type,
                {"type": "context_response", "context": context}
            )
        
        elif message.content.get("type") == "model_update":
            # Update world model based on feedback
            update_data = message.content.get("update_data", {})
            if "entity" in update_data:
                entity_data = update_data["entity"]
                self.world_model.add_entity(entity_data["id"], entity_data["properties"])
            
            LOG.info(f"MBR {self.agent_id} updated world model")
            return None
        
        return None
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get a summary of the current world model."""
        return {
            "entities_count": len(self.world_model.entities),
            "relationships_count": sum(len(rels) for rels in self.world_model.relationships.values()),
            "patterns_count": len(self.world_model.patterns),
            "decision_history_length": len(self.decision_history),
            "average_confidence": sum(d["decision"].get("confidence", 0) for d in self.decision_history) / len(self.decision_history) if self.decision_history else 0
        }