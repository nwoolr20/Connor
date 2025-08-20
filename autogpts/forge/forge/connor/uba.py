"""
Utility-Based Agent (UBA)

UBAs assign values or utilities to different outcomes and choose actions based
on utilities. They optimize decision-making by considering multiple factors
and their relative importance.
"""

from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import math
from .base import BaseConnorAgent, AgentMessage, AgentType, AgentConfig
from forge.sdk import ForgeLogger

LOG = ForgeLogger(__name__)


class UtilityFunction(Enum):
    """Types of utility functions."""
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    EXPONENTIAL = "exponential"
    SIGMOID = "sigmoid"
    CUSTOM = "custom"


@dataclass
class UtilityFactor:
    """Represents a factor in utility calculation."""
    factor_id: str
    name: str
    weight: float
    utility_function: UtilityFunction = UtilityFunction.LINEAR
    min_value: float = 0.0
    max_value: float = 1.0
    current_value: float = 0.5


@dataclass
class Alternative:
    """Represents an alternative choice for decision making."""
    alternative_id: str
    description: str
    attributes: Dict[str, float]
    estimated_outcomes: Dict[str, Any]
    risks: List[str] = None
    opportunities: List[str] = None
    
    def __post_init__(self):
        if self.risks is None:
            self.risks = []
        if self.opportunities is None:
            self.opportunities = []


@dataclass
class Decision:
    """Represents a decision made by the UBA."""
    decision_id: str
    alternatives: List[Alternative]
    selected_alternative: str
    utility_scores: Dict[str, float]
    reasoning: List[str]
    confidence: float
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class UtilityBasedAgent(BaseConnorAgent):
    """
    Utility-Based Agent that makes decisions by evaluating utilities of different options.
    
    UBAs receive input from various sources and optimize decisions based on assigned
    values and utilities to achieve the best possible outcomes.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.utility_factors = {}
        self.alternatives_history = []
        self.decision_history = []
        self.preferences = self._initialize_preferences()
        self.utility_functions = self._initialize_utility_functions()
        
    def _initialize_preferences(self) -> Dict[str, float]:
        """Initialize default preferences for decision making."""
        return {
            "accuracy": 0.9,
            "speed": 0.7,
            "efficiency": 0.8,
            "cost": 0.6,
            "risk_tolerance": 0.5,
            "innovation": 0.7,
            "reliability": 0.9,
            "user_satisfaction": 0.95
        }
    
    def _initialize_utility_functions(self) -> Dict[UtilityFunction, Callable]:
        """Initialize utility calculation functions."""
        return {
            UtilityFunction.LINEAR: lambda x, min_val, max_val: (x - min_val) / (max_val - min_val) if max_val != min_val else 0.5,
            UtilityFunction.LOGARITHMIC: lambda x, min_val, max_val: math.log(1 + (x - min_val)) / math.log(1 + (max_val - min_val)) if max_val != min_val else 0.5,
            UtilityFunction.EXPONENTIAL: lambda x, min_val, max_val: (math.exp(x - min_val) - 1) / (math.exp(max_val - min_val) - 1) if max_val != min_val else 0.5,
            UtilityFunction.SIGMOID: lambda x, min_val, max_val: 1 / (1 + math.exp(-((x - min_val) / (max_val - min_val) - 0.5) * 10)) if max_val != min_val else 0.5
        }
    
    async def process_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Process input by evaluating utilities and making optimal decisions.
        
        Args:
            input_data: Input data to process and make decisions about
            
        Returns:
            Response with utility analysis and optimal decision
        """
        # Extract relevant information
        if isinstance(input_data, dict):
            original_input = input_data.get("original_input", "")
            goal = input_data.get("goal", {})
            plan = input_data.get("plan", {})
            context = input_data.get("context", {})
            analysis = input_data.get("analysis", {})
        else:
            original_input = str(input_data)
            goal = {}
            plan = {}
            context = {}
            analysis = {}
        
        # Generate alternatives for the decision
        alternatives = self._generate_alternatives(input_data, context)
        
        # Define utility factors for this decision
        utility_factors = self._define_utility_factors(input_data, context)
        
        # Calculate utilities for each alternative
        utility_scores = self._calculate_utilities(alternatives, utility_factors)
        
        # Make the optimal decision
        decision = self._make_optimal_decision(alternatives, utility_scores)
        
        # Assess decision quality and confidence
        quality_assessment = self._assess_decision_quality(decision, alternatives, utility_scores)
        
        # Create response
        response = {
            "original_input": original_input,
            "alternatives_considered": len(alternatives),
            "utility_factors": {uf.factor_id: uf.weight for uf in utility_factors.values()},
            "utility_scores": utility_scores,
            "selected_alternative": decision.selected_alternative,
            "decision_reasoning": decision.reasoning,
            "confidence": decision.confidence,
            "quality_assessment": quality_assessment,
            "processed_by": self.agent_id,
            "agent_type": self.agent_type.value,
            "optimization_applied": True,
            "expected_utility": utility_scores.get(decision.selected_alternative, 0.0)
        }
        
        # Store decision and alternatives
        self.decision_history.append(decision)
        self.alternatives_history.extend(alternatives)
        
        # Add to memory
        self.add_to_memory({
            "decision_id": decision.decision_id,
            "selected_alternative": decision.selected_alternative,
            "utility_score": utility_scores.get(decision.selected_alternative, 0.0),
            "confidence": decision.confidence,
            "timestamp": decision.timestamp
        })
        
        LOG.info(f"UBA {self.agent_id} made decision: {decision.selected_alternative} (utility: {utility_scores.get(decision.selected_alternative, 0.0):.3f})")
        
        return response
    
    def _generate_alternatives(self, input_data: Any, context: Dict[str, Any]) -> List[Alternative]:
        """Generate alternative approaches for the given input."""
        alternatives = []
        
        if isinstance(input_data, dict):
            # Generate alternatives based on input type and context
            input_type = input_data.get("input_type", "general")
            analysis = input_data.get("analysis", {})
            
            if input_type == "question":
                alternatives = self._generate_information_alternatives(input_data, context)
            elif input_type == "task":
                alternatives = self._generate_task_alternatives(input_data, context)
            elif input_type == "request":
                alternatives = self._generate_request_alternatives(input_data, context)
            else:
                alternatives = self._generate_general_alternatives(input_data, context)
        else:
            alternatives = self._generate_general_alternatives(input_data, context)
        
        return alternatives
    
    def _generate_information_alternatives(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> List[Alternative]:
        """Generate alternatives for information requests."""
        alternatives = [
            Alternative(
                alternative_id="comprehensive_search",
                description="Comprehensive search across all available sources",
                attributes={
                    "accuracy": 0.9,
                    "completeness": 0.95,
                    "speed": 0.6,
                    "cost": 0.8
                },
                estimated_outcomes={"quality": "high", "time": "moderate"}
            ),
            Alternative(
                alternative_id="quick_lookup",
                description="Quick lookup from cached knowledge",
                attributes={
                    "accuracy": 0.75,
                    "completeness": 0.7,
                    "speed": 0.95,
                    "cost": 0.3
                },
                estimated_outcomes={"quality": "good", "time": "fast"}
            ),
            Alternative(
                alternative_id="contextual_synthesis",
                description="Synthesize answer from available context",
                attributes={
                    "accuracy": 0.8,
                    "completeness": 0.8,
                    "speed": 0.8,
                    "cost": 0.5
                },
                estimated_outcomes={"quality": "good", "time": "moderate"}
            )
        ]
        
        # Adjust alternatives based on context
        if context.get("relevant_entities"):
            alternatives[2].attributes["accuracy"] += 0.1
        
        return alternatives
    
    def _generate_task_alternatives(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> List[Alternative]:
        """Generate alternatives for task execution."""
        alternatives = [
            Alternative(
                alternative_id="step_by_step",
                description="Execute task step by step with verification",
                attributes={
                    "reliability": 0.9,
                    "accuracy": 0.95,
                    "speed": 0.6,
                    "efficiency": 0.7
                },
                estimated_outcomes={"success_rate": "high", "time": "longer"}
            ),
            Alternative(
                alternative_id="parallel_execution",
                description="Execute multiple parts in parallel",
                attributes={
                    "reliability": 0.75,
                    "accuracy": 0.8,
                    "speed": 0.9,
                    "efficiency": 0.85
                },
                estimated_outcomes={"success_rate": "good", "time": "faster"},
                risks=["coordination_complexity", "resource_conflicts"]
            ),
            Alternative(
                alternative_id="optimized_approach",
                description="Use optimized algorithms and shortcuts",
                attributes={
                    "reliability": 0.8,
                    "accuracy": 0.85,
                    "speed": 0.85,
                    "efficiency": 0.9
                },
                estimated_outcomes={"success_rate": "good", "time": "fast"},
                opportunities=["learning_optimization", "pattern_reuse"]
            )
        ]
        
        return alternatives
    
    def _generate_request_alternatives(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> List[Alternative]:
        """Generate alternatives for general requests."""
        alternatives = [
            Alternative(
                alternative_id="direct_fulfillment",
                description="Directly fulfill the request as stated",
                attributes={
                    "user_satisfaction": 0.9,
                    "accuracy": 0.85,
                    "speed": 0.8,
                    "innovation": 0.5
                },
                estimated_outcomes={"user_response": "satisfied"}
            ),
            Alternative(
                alternative_id="enhanced_fulfillment",
                description="Fulfill request with additional value-added features",
                attributes={
                    "user_satisfaction": 0.95,
                    "accuracy": 0.9,
                    "speed": 0.7,
                    "innovation": 0.8
                },
                estimated_outcomes={"user_response": "delighted"}
            ),
            Alternative(
                alternative_id="clarification_first",
                description="Ask for clarification before proceeding",
                attributes={
                    "user_satisfaction": 0.8,
                    "accuracy": 0.95,
                    "speed": 0.5,
                    "innovation": 0.6
                },
                estimated_outcomes={"user_response": "engaged"}
            )
        ]
        
        return alternatives
    
    def _generate_general_alternatives(self, input_data: Any, context: Dict[str, Any]) -> List[Alternative]:
        """Generate general alternatives for any input."""
        alternatives = [
            Alternative(
                alternative_id="standard_processing",
                description="Apply standard processing approach",
                attributes={
                    "reliability": 0.8,
                    "speed": 0.8,
                    "cost": 0.5,
                    "accuracy": 0.8
                },
                estimated_outcomes={"result": "standard"}
            ),
            Alternative(
                alternative_id="conservative_approach",
                description="Use conservative, low-risk approach",
                attributes={
                    "reliability": 0.95,
                    "speed": 0.6,
                    "cost": 0.7,
                    "accuracy": 0.9
                },
                estimated_outcomes={"result": "safe"}
            ),
            Alternative(
                alternative_id="innovative_approach",
                description="Try innovative, potentially better approach",
                attributes={
                    "reliability": 0.7,
                    "speed": 0.8,
                    "cost": 0.6,
                    "accuracy": 0.75,
                    "innovation": 0.9
                },
                estimated_outcomes={"result": "potentially_better"},
                risks=["unknown_outcomes", "higher_complexity"]
            )
        ]
        
        return alternatives
    
    def _define_utility_factors(self, input_data: Any, context: Dict[str, Any]) -> Dict[str, UtilityFactor]:
        """Define utility factors relevant to the current decision."""
        factors = {}
        
        # Base factors always considered
        base_factors = [
            ("accuracy", "Accuracy of results", 0.9),
            ("speed", "Speed of execution", 0.7),
            ("reliability", "Reliability of approach", 0.8),
            ("efficiency", "Resource efficiency", 0.6)
        ]
        
        for factor_id, name, weight in base_factors:
            factors[factor_id] = UtilityFactor(
                factor_id=factor_id,
                name=name,
                weight=weight * self.preferences.get(factor_id, 0.5),
                utility_function=UtilityFunction.LINEAR
            )
        
        # Add context-specific factors
        if isinstance(input_data, dict):
            input_type = input_data.get("input_type", "general")
            
            if input_type == "question":
                factors["completeness"] = UtilityFactor(
                    factor_id="completeness",
                    name="Completeness of answer",
                    weight=0.8 * self.preferences.get("accuracy", 0.9),
                    utility_function=UtilityFunction.LOGARITHMIC
                )
            elif input_type == "task":
                factors["user_satisfaction"] = UtilityFactor(
                    factor_id="user_satisfaction",
                    name="User satisfaction",
                    weight=0.95 * self.preferences.get("user_satisfaction", 0.95),
                    utility_function=UtilityFunction.SIGMOID
                )
            
            # Check for innovation requirements
            analysis = input_data.get("analysis", {})
            if analysis.get("complexity") == "high":
                factors["innovation"] = UtilityFactor(
                    factor_id="innovation",
                    name="Innovation level",
                    weight=0.7 * self.preferences.get("innovation", 0.7),
                    utility_function=UtilityFunction.EXPONENTIAL
                )
        
        return factors
    
    def _calculate_utilities(self, alternatives: List[Alternative], 
                           utility_factors: Dict[str, UtilityFactor]) -> Dict[str, float]:
        """Calculate utility scores for all alternatives."""
        utilities = {}
        
        for alternative in alternatives:
            total_utility = 0.0
            total_weight = 0.0
            
            for factor_id, factor in utility_factors.items():
                if factor_id in alternative.attributes:
                    # Get attribute value
                    value = alternative.attributes[factor_id]
                    
                    # Calculate normalized utility using the specified function
                    utility_func = self.utility_functions.get(
                        factor.utility_function, 
                        self.utility_functions[UtilityFunction.LINEAR]
                    )
                    
                    normalized_utility = utility_func(value, factor.min_value, factor.max_value)
                    
                    # Weight the utility
                    weighted_utility = normalized_utility * factor.weight
                    total_utility += weighted_utility
                    total_weight += factor.weight
            
            # Apply risk and opportunity adjustments
            risk_penalty = len(alternative.risks) * 0.05  # 5% penalty per risk
            opportunity_bonus = len(alternative.opportunities) * 0.03  # 3% bonus per opportunity
            
            final_utility = (total_utility / total_weight if total_weight > 0 else 0) - risk_penalty + opportunity_bonus
            utilities[alternative.alternative_id] = max(0.0, min(1.0, final_utility))
        
        return utilities
    
    def _make_optimal_decision(self, alternatives: List[Alternative], 
                             utility_scores: Dict[str, float]) -> Decision:
        """Make the optimal decision based on utility scores."""
        # Find the alternative with highest utility
        best_alternative_id = max(utility_scores.items(), key=lambda x: x[1])[0]
        best_alternative = next(alt for alt in alternatives if alt.alternative_id == best_alternative_id)
        
        # Generate reasoning
        reasoning = self._generate_decision_reasoning(best_alternative, alternatives, utility_scores)
        
        # Calculate confidence based on utility gap
        sorted_utilities = sorted(utility_scores.values(), reverse=True)
        if len(sorted_utilities) > 1:
            utility_gap = sorted_utilities[0] - sorted_utilities[1]
            confidence = min(0.5 + utility_gap, 1.0)  # Base confidence + utility gap
        else:
            confidence = 0.8  # Default confidence for single alternative
        
        # Adjust confidence based on absolute utility score
        best_utility = utility_scores[best_alternative_id]
        if best_utility > 0.8:
            confidence += 0.1
        elif best_utility < 0.5:
            confidence -= 0.2
        
        confidence = max(0.1, min(1.0, confidence))
        
        decision = Decision(
            decision_id=f"decision_{len(self.decision_history)}_{int(time.time())}",
            alternatives=alternatives,
            selected_alternative=best_alternative_id,
            utility_scores=utility_scores,
            reasoning=reasoning,
            confidence=confidence
        )
        
        return decision
    
    def _generate_decision_reasoning(self, selected_alternative: Alternative, 
                                   all_alternatives: List[Alternative],
                                   utility_scores: Dict[str, float]) -> List[str]:
        """Generate reasoning for the decision."""
        reasoning = []
        
        selected_utility = utility_scores[selected_alternative.alternative_id]
        
        # Main selection reason
        reasoning.append(f"Selected '{selected_alternative.description}' with utility score {selected_utility:.3f}")
        
        # Compare with other alternatives
        for alt in all_alternatives:
            if alt.alternative_id != selected_alternative.alternative_id:
                alt_utility = utility_scores[alt.alternative_id]
                if selected_utility > alt_utility:
                    reasoning.append(f"Outperformed '{alt.description}' (utility: {alt_utility:.3f})")
        
        # Highlight key strengths
        best_attributes = sorted(selected_alternative.attributes.items(), key=lambda x: x[1], reverse=True)[:3]
        for attr, value in best_attributes:
            reasoning.append(f"High {attr}: {value:.2f}")
        
        # Note risks if any
        if selected_alternative.risks:
            reasoning.append(f"Accepts risks: {', '.join(selected_alternative.risks)}")
        
        # Note opportunities if any
        if selected_alternative.opportunities:
            reasoning.append(f"Leverages opportunities: {', '.join(selected_alternative.opportunities)}")
        
        return reasoning
    
    def _assess_decision_quality(self, decision: Decision, alternatives: List[Alternative],
                               utility_scores: Dict[str, float]) -> Dict[str, Any]:
        """Assess the quality of the decision made."""
        assessment = {
            "decision_quality": "good",  # Default
            "utility_distribution": {},
            "risk_assessment": "moderate",
            "opportunity_assessment": "moderate",
            "confidence_level": decision.confidence
        }
        
        # Analyze utility distribution
        utilities = list(utility_scores.values())
        assessment["utility_distribution"] = {
            "max": max(utilities),
            "min": min(utilities),
            "average": sum(utilities) / len(utilities),
            "spread": max(utilities) - min(utilities)
        }
        
        # Assess decision quality based on best utility
        best_utility = max(utilities)
        if best_utility > 0.8:
            assessment["decision_quality"] = "excellent"
        elif best_utility > 0.6:
            assessment["decision_quality"] = "good"
        elif best_utility > 0.4:
            assessment["decision_quality"] = "fair"
        else:
            assessment["decision_quality"] = "poor"
        
        # Risk assessment
        selected_alt = next(alt for alt in alternatives if alt.alternative_id == decision.selected_alternative)
        if len(selected_alt.risks) == 0:
            assessment["risk_assessment"] = "low"
        elif len(selected_alt.risks) <= 2:
            assessment["risk_assessment"] = "moderate"
        else:
            assessment["risk_assessment"] = "high"
        
        # Opportunity assessment
        if len(selected_alt.opportunities) == 0:
            assessment["opportunity_assessment"] = "low"
        elif len(selected_alt.opportunities) <= 2:
            assessment["opportunity_assessment"] = "moderate"
        else:
            assessment["opportunity_assessment"] = "high"
        
        return assessment
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle messages from other agents."""
        if message.content.get("type") == "preference_update":
            # Update preferences based on feedback
            new_preferences = message.content.get("preferences", {})
            
            for pref, value in new_preferences.items():
                if pref in self.preferences:
                    # Gradually adjust preferences
                    self.preferences[pref] = (self.preferences[pref] + value) / 2
            
            LOG.info(f"UBA {self.agent_id} updated preferences")
            
            return self.send_message(
                message.sender_id,
                message.sender_type,
                {"type": "preference_update_ack", "updated_preferences": list(new_preferences.keys())}
            )
        
        elif message.content.get("type") == "decision_feedback":
            # Process feedback on previous decisions
            decision_id = message.content.get("decision_id")
            feedback = message.content.get("feedback", {})
            
            await self._process_decision_feedback(decision_id, feedback)
            
            return None
        
        elif message.content.get("type") == "utility_comparison":
            # Compare utilities with another agent's approach
            other_utilities = message.content.get("utilities", {})
            comparison = self._compare_utilities(other_utilities)
            
            return self.send_message(
                message.sender_id,
                message.sender_type,
                {"type": "utility_comparison_result", "comparison": comparison}
            )
        
        return None
    
    async def _process_decision_feedback(self, decision_id: str, feedback: Dict[str, Any]) -> None:
        """Process feedback on a previous decision to improve future decisions."""
        # Find the decision
        decision = None
        for dec in self.decision_history:
            if dec.decision_id == decision_id:
                decision = dec
                break
        
        if not decision:
            return
        
        # Extract feedback metrics
        actual_outcome = feedback.get("actual_outcome", {})
        satisfaction = feedback.get("satisfaction", 0.5)
        issues = feedback.get("issues", [])
        successes = feedback.get("successes", [])
        
        # Adjust preferences based on feedback
        if satisfaction > 0.8:
            # Positive feedback - reinforce successful factors
            selected_alt = next(alt for alt in decision.alternatives if alt.alternative_id == decision.selected_alternative)
            for attr, value in selected_alt.attributes.items():
                if attr in self.preferences and value > 0.7:
                    self.preferences[attr] = min(self.preferences[attr] + 0.05, 1.0)
        
        elif satisfaction < 0.4:
            # Negative feedback - adjust preferences
            for issue in issues:
                if issue in self.preferences:
                    self.preferences[issue] = max(self.preferences[issue] - 0.05, 0.0)
        
        LOG.info(f"UBA {self.agent_id} processed feedback for decision {decision_id}")
    
    def _compare_utilities(self, other_utilities: Dict[str, float]) -> Dict[str, Any]:
        """Compare utilities with another agent's approach."""
        if not self.decision_history:
            return {"comparison": "no_data"}
        
        latest_decision = self.decision_history[-1]
        my_utilities = latest_decision.utility_scores
        
        comparison = {
            "my_max_utility": max(my_utilities.values()) if my_utilities else 0,
            "other_max_utility": max(other_utilities.values()) if other_utilities else 0,
            "difference": 0,
            "better_alternatives": [],
            "analysis": []
        }
        
        if my_utilities and other_utilities:
            comparison["difference"] = comparison["my_max_utility"] - comparison["other_max_utility"]
            
            # Find alternatives where other agent performed better
            for alt_id, other_util in other_utilities.items():
                my_util = my_utilities.get(alt_id, 0)
                if other_util > my_util:
                    comparison["better_alternatives"].append({
                        "alternative": alt_id,
                        "my_utility": my_util,
                        "other_utility": other_util
                    })
            
            # Generate analysis
            if comparison["difference"] > 0.1:
                comparison["analysis"].append("My approach yielded significantly better utilities")
            elif comparison["difference"] < -0.1:
                comparison["analysis"].append("Other approach yielded significantly better utilities")
            else:
                comparison["analysis"].append("Both approaches yielded similar utilities")
        
        return comparison
    
    def update_preferences(self, new_preferences: Dict[str, float]) -> None:
        """Update agent preferences for future decisions."""
        for pref, value in new_preferences.items():
            if 0.0 <= value <= 1.0:
                self.preferences[pref] = value
        
        LOG.info(f"UBA {self.agent_id} updated preferences: {list(new_preferences.keys())}")
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get comprehensive decision-making statistics."""
        if not self.decision_history:
            return {"total_decisions": 0}
        
        utilities = [max(dec.utility_scores.values()) for dec in self.decision_history]
        confidences = [dec.confidence for dec in self.decision_history]
        
        # Count alternatives by type
        alternative_counts = {}
        for decision in self.decision_history:
            selected = decision.selected_alternative
            alternative_counts[selected] = alternative_counts.get(selected, 0) + 1
        
        return {
            "total_decisions": len(self.decision_history),
            "average_utility": sum(utilities) / len(utilities),
            "max_utility": max(utilities),
            "min_utility": min(utilities),
            "average_confidence": sum(confidences) / len(confidences),
            "current_preferences": self.preferences.copy(),
            "popular_alternatives": dict(sorted(alternative_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "recent_performance": {
                "last_5_avg_utility": sum(utilities[-5:]) / min(len(utilities), 5),
                "last_5_avg_confidence": sum(confidences[-5:]) / min(len(confidences), 5)
            }
        }