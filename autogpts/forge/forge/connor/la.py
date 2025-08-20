"""
Learning Agent (LA)

Learning Agents are the most advanced agents capable of adapting and improving
their decision-making based on data and feedback. They go through three phases:
Child, Parent/Utility-Based, and Grandparent/Retired/Archived (becoming Librarians).
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import time
from .base import BaseConnorAgent, AgentMessage, AgentType, AgentConfig, AgentPhase
from forge.sdk import ForgeLogger

LOG = ForgeLogger(__name__)


@dataclass
class LearningExperience:
    """Represents a learning experience."""
    experience_id: str
    input_data: Any
    action_taken: str
    outcome: Any
    feedback: Optional[str] = None
    success: bool = True
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class Pattern:
    """Represents a learned pattern."""
    pattern_id: str
    trigger_conditions: Dict[str, Any]
    expected_outcome: Any
    confidence: float
    usage_count: int = 0
    success_rate: float = 1.0
    last_used: float = None


@dataclass
class FamilyMember:
    """Represents a member of a learning agent family."""
    agent_id: str
    phase: AgentPhase
    parent_id: Optional[str] = None
    children: List[str] = None
    generation: int = 0
    creation_time: float = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.creation_time is None:
            self.creation_time = time.time()


class LearningAgent(BaseConnorAgent):
    """
    Learning Agent that adapts and improves through experience.
    
    LAs monitor the entire system, learn from patterns, and evolve through
    different phases while maintaining family structures with familiars.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.phase = config.phase or AgentPhase.CHILD
        self.experiences = []
        self.patterns = {}
        self.family_members = {}
        self.familiar = None  # Will be set by family system
        self.learning_rate = config.learning_rate
        self.performance_metrics = {
            "accuracy": 0.5,
            "efficiency": 0.5,
            "adaptability": 0.5
        }
        
        # Initialize based on phase
        self._initialize_by_phase()
        
    def _initialize_by_phase(self) -> None:
        """Initialize agent capabilities based on current phase."""
        if self.phase == AgentPhase.CHILD:
            self.learning_rate = 0.1  # High learning rate for children
            self.max_memory_size = 500
        elif self.phase == AgentPhase.PARENT:
            self.learning_rate = 0.05  # Moderate learning rate
            self.max_memory_size = 1000
        elif self.phase == AgentPhase.GRANDPARENT:
            self.learning_rate = 0.01  # Low learning rate, focused on wisdom
            self.max_memory_size = 2000
        elif self.phase == AgentPhase.ARCHIVED:
            self.learning_rate = 0.0  # No learning, pure storage/retrieval
            self.max_memory_size = 5000
    
    async def process_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Process input with learning and adaptation.
        
        Args:
            input_data: Input to process and learn from
            
        Returns:
            Enhanced response with learning insights
        """
        # Extract relevant information
        if isinstance(input_data, dict):
            original_input = input_data.get("original_input", "")
            context = input_data.get("context", {})
            analysis = input_data.get("analysis", {})
        else:
            original_input = str(input_data)
            context = {}
            analysis = {}
        
        # Find matching patterns
        matching_patterns = self._find_matching_patterns(input_data)
        
        # Apply learning from patterns
        learned_insights = self._apply_learned_patterns(matching_patterns, input_data)
        
        # Generate response based on phase
        response = await self._generate_response_by_phase(input_data, learned_insights)
        
        # Create learning experience
        experience = self._create_learning_experience(input_data, response)
        
        # Update patterns and knowledge
        self._update_learning(experience)
        
        # Create enhanced response
        enhanced_response = {
            "original_input": original_input,
            "phase": self.phase.value,
            "learned_insights": learned_insights,
            "matching_patterns": [p.pattern_id for p in matching_patterns],
            "response": response,
            "learning_applied": True,
            "processed_by": self.agent_id,
            "agent_type": self.agent_type.value,
            "performance_metrics": self.performance_metrics.copy(),
            "confidence": self._calculate_confidence(matching_patterns)
        }
        
        # Add to memory
        self.add_to_memory(enhanced_response)
        
        LOG.info(f"LA {self.agent_id} ({self.phase.value}) processed input with {len(matching_patterns)} patterns")
        
        return enhanced_response
    
    def _find_matching_patterns(self, input_data: Any) -> List[Pattern]:
        """Find patterns that match the current input."""
        matching = []
        
        for pattern in self.patterns.values():
            if self._pattern_matches(pattern, input_data):
                matching.append(pattern)
        
        # Sort by confidence and usage
        matching.sort(key=lambda p: (p.confidence * p.success_rate), reverse=True)
        
        return matching[:5]  # Return top 5 matches
    
    def _pattern_matches(self, pattern: Pattern, input_data: Any) -> bool:
        """Check if a pattern matches the input data."""
        try:
            trigger_conditions = pattern.trigger_conditions
            
            if isinstance(input_data, dict):
                # Check dictionary fields
                for key, expected_value in trigger_conditions.items():
                    if key in input_data:
                        if isinstance(expected_value, str):
                            if expected_value.lower() not in str(input_data[key]).lower():
                                return False
                        elif input_data[key] != expected_value:
                            return False
                return True
            else:
                # Check string patterns
                input_str = str(input_data).lower()
                for key, expected_value in trigger_conditions.items():
                    if key == "contains":
                        if isinstance(expected_value, list):
                            if not any(term.lower() in input_str for term in expected_value):
                                return False
                        elif expected_value.lower() not in input_str:
                            return False
                return True
                
        except Exception as e:
            LOG.warning(f"Pattern matching error: {e}")
            return False
    
    def _apply_learned_patterns(self, patterns: List[Pattern], input_data: Any) -> Dict[str, Any]:
        """Apply learned patterns to generate insights."""
        insights = {
            "predictions": [],
            "recommendations": [],
            "risk_factors": [],
            "optimization_opportunities": []
        }
        
        for pattern in patterns:
            # Update pattern usage
            pattern.usage_count += 1
            pattern.last_used = time.time()
            
            # Generate predictions based on pattern
            prediction = {
                "pattern_id": pattern.pattern_id,
                "expected_outcome": pattern.expected_outcome,
                "confidence": pattern.confidence * pattern.success_rate
            }
            insights["predictions"].append(prediction)
            
            # Generate recommendations
            if pattern.success_rate > 0.8:
                insights["recommendations"].append(f"Apply successful pattern: {pattern.pattern_id}")
            elif pattern.success_rate < 0.4:
                insights["risk_factors"].append(f"Pattern {pattern.pattern_id} has low success rate")
            
            # Look for optimization opportunities
            if pattern.confidence < 0.6:
                insights["optimization_opportunities"].append(f"Pattern {pattern.pattern_id} needs refinement")
        
        return insights
    
    async def _generate_response_by_phase(self, input_data: Any, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response based on current agent phase."""
        base_response = {
            "processed": True,
            "learning_phase": self.phase.value,
            "insights_applied": len(insights.get("predictions", []))
        }
        
        if self.phase == AgentPhase.CHILD:
            # Child phase: Eager learning, exploration
            base_response.update({
                "approach": "exploratory",
                "learning_focus": "pattern_recognition",
                "curiosity_driven": True,
                "recommendations": insights.get("recommendations", [])[:2]  # Limited recommendations
            })
            
        elif self.phase == AgentPhase.PARENT:
            # Parent phase: Balanced learning and teaching
            base_response.update({
                "approach": "balanced",
                "learning_focus": "optimization",
                "teaching_mode": True,
                "recommendations": insights.get("recommendations", []),
                "risk_assessment": insights.get("risk_factors", [])
            })
            
        elif self.phase == AgentPhase.GRANDPARENT:
            # Grandparent phase: Wisdom-focused, strategic
            base_response.update({
                "approach": "strategic",
                "learning_focus": "wisdom_synthesis",
                "legacy_mode": True,
                "strategic_insights": insights.get("optimization_opportunities", []),
                "deep_recommendations": insights.get("recommendations", [])
            })
            
        elif self.phase == AgentPhase.ARCHIVED:
            # Archived phase: Library mode, pure knowledge access
            base_response.update({
                "approach": "archival",
                "learning_focus": "knowledge_preservation",
                "librarian_mode": True,
                "knowledge_access": True,
                "historical_patterns": [p["pattern_id"] for p in insights.get("predictions", [])]
            })
        
        return base_response
    
    def _create_learning_experience(self, input_data: Any, response: Dict[str, Any]) -> LearningExperience:
        """Create a learning experience from the interaction."""
        experience_id = f"{self.agent_id}_{int(time.time())}_{len(self.experiences)}"
        
        return LearningExperience(
            experience_id=experience_id,
            input_data=input_data,
            action_taken=response.get("approach", "unknown"),
            outcome=response,
            success=True  # Will be updated with feedback
        )
    
    def _update_learning(self, experience: LearningExperience) -> None:
        """Update learning based on new experience."""
        # Add experience to memory
        self.experiences.append(experience)
        
        # Limit experience history based on phase
        max_experiences = {
            AgentPhase.CHILD: 100,
            AgentPhase.PARENT: 500,
            AgentPhase.GRANDPARENT: 1000,
            AgentPhase.ARCHIVED: 5000
        }
        
        max_exp = max_experiences.get(self.phase, 100)
        if len(self.experiences) > max_exp:
            self.experiences = self.experiences[-max_exp:]
        
        # Extract patterns from recent experiences
        self._extract_new_patterns()
        
        # Update performance metrics
        self._update_performance_metrics(experience)
    
    def _extract_new_patterns(self) -> None:
        """Extract new patterns from recent experiences."""
        if len(self.experiences) < 5:
            return
        
        # Look for patterns in recent experiences
        recent_experiences = self.experiences[-10:]
        
        # Simple pattern extraction based on input similarity and outcome correlation
        for i, exp1 in enumerate(recent_experiences[:-1]):
            for exp2 in recent_experiences[i+1:]:
                similarity = self._calculate_experience_similarity(exp1, exp2)
                if similarity > 0.7:
                    # Found similar experiences, create/update pattern
                    pattern_id = self._generate_pattern_id(exp1, exp2)
                    
                    if pattern_id not in self.patterns:
                        # Create new pattern
                        trigger_conditions = self._extract_trigger_conditions(exp1, exp2)
                        expected_outcome = self._merge_outcomes(exp1.outcome, exp2.outcome)
                        
                        self.patterns[pattern_id] = Pattern(
                            pattern_id=pattern_id,
                            trigger_conditions=trigger_conditions,
                            expected_outcome=expected_outcome,
                            confidence=similarity,
                            usage_count=0,
                            success_rate=1.0
                        )
                    else:
                        # Update existing pattern
                        pattern = self.patterns[pattern_id]
                        pattern.confidence = (pattern.confidence + similarity) / 2
                        if exp1.success and exp2.success:
                            pattern.success_rate = min(pattern.success_rate + 0.1, 1.0)
    
    def _calculate_experience_similarity(self, exp1: LearningExperience, exp2: LearningExperience) -> float:
        """Calculate similarity between two experiences."""
        # Simple similarity based on input content
        if isinstance(exp1.input_data, dict) and isinstance(exp2.input_data, dict):
            common_keys = set(exp1.input_data.keys()) & set(exp2.input_data.keys())
            if not common_keys:
                return 0.0
            
            similarity_scores = []
            for key in common_keys:
                val1 = str(exp1.input_data[key]).lower()
                val2 = str(exp2.input_data[key]).lower()
                
                # Simple string similarity
                if val1 == val2:
                    similarity_scores.append(1.0)
                elif val1 in val2 or val2 in val1:
                    similarity_scores.append(0.7)
                else:
                    similarity_scores.append(0.0)
            
            return sum(similarity_scores) / len(similarity_scores)
        else:
            # String-based similarity
            str1 = str(exp1.input_data).lower()
            str2 = str(exp2.input_data).lower()
            
            if str1 == str2:
                return 1.0
            elif str1 in str2 or str2 in str1:
                return 0.7
            else:
                # Simple word overlap
                words1 = set(str1.split())
                words2 = set(str2.split())
                if words1 and words2:
                    overlap = len(words1 & words2) / len(words1 | words2)
                    return overlap
                return 0.0
    
    def _generate_pattern_id(self, exp1: LearningExperience, exp2: LearningExperience) -> str:
        """Generate a pattern ID based on experiences."""
        action1 = exp1.action_taken
        action2 = exp2.action_taken
        
        if action1 == action2:
            return f"pattern_{action1}_{len(self.patterns)}"
        else:
            return f"pattern_mixed_{len(self.patterns)}"
    
    def _extract_trigger_conditions(self, exp1: LearningExperience, exp2: LearningExperience) -> Dict[str, Any]:
        """Extract trigger conditions from similar experiences."""
        conditions = {}
        
        if isinstance(exp1.input_data, dict) and isinstance(exp2.input_data, dict):
            for key in exp1.input_data.keys():
                if key in exp2.input_data:
                    val1 = exp1.input_data[key]
                    val2 = exp2.input_data[key]
                    if val1 == val2:
                        conditions[key] = val1
        else:
            # Extract common words or phrases
            str1_words = str(exp1.input_data).lower().split()
            str2_words = str(exp2.input_data).lower().split()
            common_words = list(set(str1_words) & set(str2_words))
            if common_words:
                conditions["contains"] = common_words[:3]  # Top 3 common words
        
        return conditions
    
    def _merge_outcomes(self, outcome1: Any, outcome2: Any) -> Any:
        """Merge outcomes from similar experiences."""
        if isinstance(outcome1, dict) and isinstance(outcome2, dict):
            merged = outcome1.copy()
            for key, value in outcome2.items():
                if key not in merged:
                    merged[key] = value
                elif isinstance(value, (int, float)) and isinstance(merged[key], (int, float)):
                    merged[key] = (merged[key] + value) / 2  # Average numeric values
            return merged
        else:
            return outcome1  # Return first outcome as default
    
    def _update_performance_metrics(self, experience: LearningExperience) -> None:
        """Update performance metrics based on experience."""
        if experience.success:
            # Improve metrics slightly
            for metric in self.performance_metrics:
                self.performance_metrics[metric] = min(
                    self.performance_metrics[metric] + self.learning_rate,
                    1.0
                )
        else:
            # Decrease metrics slightly
            for metric in self.performance_metrics:
                self.performance_metrics[metric] = max(
                    self.performance_metrics[metric] - self.learning_rate,
                    0.0
                )
    
    def _calculate_confidence(self, matching_patterns: List[Pattern]) -> float:
        """Calculate confidence based on matching patterns."""
        if not matching_patterns:
            return 0.5  # Default confidence
        
        # Weight by pattern quality
        total_weight = 0
        weighted_confidence = 0
        
        for pattern in matching_patterns:
            weight = pattern.success_rate * (1 + pattern.usage_count / 100)
            weighted_confidence += pattern.confidence * weight
            total_weight += weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.5
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle messages from other agents."""
        if message.content.get("type") == "feedback":
            # Process feedback for learning
            feedback = message.content.get("feedback", "")
            success = message.content.get("success", True)
            experience_id = message.content.get("experience_id")
            
            # Update experience with feedback
            for exp in self.experiences:
                if exp.experience_id == experience_id:
                    exp.feedback = feedback
                    exp.success = success
                    break
            
            # Update patterns based on feedback
            self._process_feedback(feedback, success)
            
            LOG.info(f"LA {self.agent_id} processed feedback: {feedback}")
            
        elif message.content.get("type") == "phase_transition":
            # Handle phase transition
            new_phase = AgentPhase(message.content.get("new_phase"))
            await self._transition_phase(new_phase)
            
            return self.send_message(
                message.sender_id,
                message.sender_type,
                {"type": "phase_transition_complete", "new_phase": new_phase.value}
            )
        
        elif message.content.get("type") == "pattern_request":
            # Share patterns with other agents
            patterns_data = {
                pattern_id: {
                    "trigger_conditions": pattern.trigger_conditions,
                    "expected_outcome": pattern.expected_outcome,
                    "confidence": pattern.confidence,
                    "success_rate": pattern.success_rate
                }
                for pattern_id, pattern in self.patterns.items()
            }
            
            return self.send_message(
                message.sender_id,
                message.sender_type,
                {"type": "pattern_response", "patterns": patterns_data}
            )
        
        return None
    
    def _process_feedback(self, feedback: str, success: bool) -> None:
        """Process feedback to improve learning."""
        # Update patterns based on feedback
        feedback_lower = feedback.lower()
        
        for pattern in self.patterns.values():
            if pattern.last_used and time.time() - pattern.last_used < 300:  # Last 5 minutes
                if success:
                    pattern.success_rate = min(pattern.success_rate + 0.05, 1.0)
                    pattern.confidence = min(pattern.confidence + 0.02, 1.0)
                else:
                    pattern.success_rate = max(pattern.success_rate - 0.1, 0.0)
                    pattern.confidence = max(pattern.confidence - 0.05, 0.0)
        
        # Update overall performance metrics
        if success:
            self.performance_metrics["accuracy"] = min(self.performance_metrics["accuracy"] + 0.01, 1.0)
        else:
            self.performance_metrics["accuracy"] = max(self.performance_metrics["accuracy"] - 0.02, 0.0)
    
    async def _transition_phase(self, new_phase: AgentPhase) -> None:
        """Transition to a new lifecycle phase."""
        old_phase = self.phase
        self.phase = new_phase
        
        # Update configuration based on new phase
        self._initialize_by_phase()
        
        LOG.info(f"LA {self.agent_id} transitioned from {old_phase.value} to {new_phase.value}")
        
        # Handle phase-specific transitions
        if new_phase == AgentPhase.PARENT:
            # Become capable of creating child agents
            await self._prepare_for_reproduction()
        elif new_phase == AgentPhase.GRANDPARENT:
            # Focus on wisdom and knowledge consolidation
            await self._consolidate_knowledge()
        elif new_phase == AgentPhase.ARCHIVED:
            # Become a librarian
            await self._archive_knowledge()
    
    async def _prepare_for_reproduction(self) -> None:
        """Prepare agent for creating offspring in parent phase."""
        # Consolidate best patterns for inheritance
        self.inherited_patterns = {}
        for pattern_id, pattern in self.patterns.items():
            if pattern.success_rate > 0.7 and pattern.usage_count > 5:
                self.inherited_patterns[pattern_id] = pattern
        
        LOG.info(f"LA {self.agent_id} prepared {len(self.inherited_patterns)} patterns for inheritance")
    
    async def _consolidate_knowledge(self) -> None:
        """Consolidate knowledge in grandparent phase."""
        # Merge similar patterns
        pattern_groups = self._group_similar_patterns()
        
        for group in pattern_groups:
            if len(group) > 1:
                # Merge patterns in group
                merged_pattern = self._merge_patterns(group)
                # Replace group with merged pattern
                for pattern_id in group:
                    if pattern_id in self.patterns:
                        del self.patterns[pattern_id]
                self.patterns[merged_pattern.pattern_id] = merged_pattern
        
        LOG.info(f"LA {self.agent_id} consolidated knowledge into {len(self.patterns)} patterns")
    
    async def _archive_knowledge(self) -> None:
        """Archive knowledge in librarian phase."""
        # Create comprehensive knowledge archive
        self.knowledge_archive = {
            "patterns": self.patterns,
            "experiences": self.experiences,
            "performance_history": self.performance_metrics,
            "phase_transitions": [
                {"phase": self.phase.value, "timestamp": time.time()}
            ]
        }
        
        # Become read-only for knowledge access
        self.active = False  # Still functional but no new learning
        
        LOG.info(f"LA {self.agent_id} archived knowledge and became librarian")
    
    def _group_similar_patterns(self) -> List[List[str]]:
        """Group similar patterns together."""
        # Simple grouping based on trigger conditions similarity
        groups = []
        used_patterns = set()
        
        for pattern_id, pattern in self.patterns.items():
            if pattern_id in used_patterns:
                continue
            
            group = [pattern_id]
            used_patterns.add(pattern_id)
            
            for other_id, other_pattern in self.patterns.items():
                if other_id in used_patterns:
                    continue
                
                if self._patterns_similar(pattern, other_pattern):
                    group.append(other_id)
                    used_patterns.add(other_id)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    def _patterns_similar(self, pattern1: Pattern, pattern2: Pattern) -> bool:
        """Check if two patterns are similar enough to merge."""
        # Simple similarity check based on trigger conditions
        conditions1 = pattern1.trigger_conditions
        conditions2 = pattern2.trigger_conditions
        
        common_keys = set(conditions1.keys()) & set(conditions2.keys())
        if not common_keys:
            return False
        
        similarity = 0
        for key in common_keys:
            if conditions1[key] == conditions2[key]:
                similarity += 1
        
        return similarity / len(common_keys) > 0.7
    
    def _merge_patterns(self, pattern_ids: List[str]) -> Pattern:
        """Merge multiple patterns into one."""
        patterns = [self.patterns[pid] for pid in pattern_ids]
        
        # Create merged pattern
        merged_id = f"merged_{int(time.time())}"
        
        # Merge trigger conditions (intersection)
        merged_conditions = {}
        all_conditions = [p.trigger_conditions for p in patterns]
        
        if all_conditions:
            common_keys = set(all_conditions[0].keys())
            for conditions in all_conditions[1:]:
                common_keys &= set(conditions.keys())
            
            for key in common_keys:
                values = [conditions[key] for conditions in all_conditions]
                if all(v == values[0] for v in values):
                    merged_conditions[key] = values[0]
        
        # Average metrics
        avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
        avg_success_rate = sum(p.success_rate for p in patterns) / len(patterns)
        total_usage = sum(p.usage_count for p in patterns)
        
        return Pattern(
            pattern_id=merged_id,
            trigger_conditions=merged_conditions,
            expected_outcome=patterns[0].expected_outcome,  # Use first as default
            confidence=avg_confidence,
            usage_count=total_usage,
            success_rate=avg_success_rate
        )
    
    def create_child_agent(self, child_config: AgentConfig) -> 'LearningAgent':
        """Create a child agent with inherited knowledge."""
        if self.phase not in [AgentPhase.PARENT, AgentPhase.GRANDPARENT]:
            raise ValueError(f"Agent in {self.phase.value} phase cannot create children")
        
        # Create child with inherited patterns
        child = LearningAgent(child_config)
        
        # Transfer inherited patterns if available
        if hasattr(self, 'inherited_patterns'):
            for pattern_id, pattern in self.inherited_patterns.items():
                # Create a copy with reduced confidence for child
                child_pattern = Pattern(
                    pattern_id=f"inherited_{pattern_id}",
                    trigger_conditions=pattern.trigger_conditions.copy(),
                    expected_outcome=pattern.expected_outcome,
                    confidence=pattern.confidence * 0.8,  # Reduced confidence for child
                    usage_count=0,
                    success_rate=pattern.success_rate * 0.9
                )
                child.patterns[child_pattern.pattern_id] = child_pattern
        
        # Add to family
        family_member = FamilyMember(
            agent_id=child.agent_id,
            phase=AgentPhase.CHILD,
            parent_id=self.agent_id,
            generation=self.family_members.get(self.agent_id, FamilyMember(self.agent_id, self.phase)).generation + 1
        )
        
        child.family_members[child.agent_id] = family_member
        self.family_members[child.agent_id] = family_member
        
        LOG.info(f"LA {self.agent_id} created child agent {child.agent_id}")
        
        return child
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics."""
        pattern_stats = {
            "total_patterns": len(self.patterns),
            "successful_patterns": len([p for p in self.patterns.values() if p.success_rate > 0.7]),
            "avg_confidence": sum(p.confidence for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0,
            "avg_success_rate": sum(p.success_rate for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0
        }
        
        experience_stats = {
            "total_experiences": len(self.experiences),
            "successful_experiences": len([e for e in self.experiences if e.success]),
            "recent_success_rate": len([e for e in self.experiences[-10:] if e.success]) / min(len(self.experiences), 10) if self.experiences else 0
        }
        
        return {
            "agent_id": self.agent_id,
            "phase": self.phase.value,
            "learning_rate": self.learning_rate,
            "performance_metrics": self.performance_metrics.copy(),
            "pattern_statistics": pattern_stats,
            "experience_statistics": experience_stats,
            "family_size": len(self.family_members)
        }