"""
Goal-Based Agent-Planner (GAP)

GAPs have specific objectives or goals they aim to achieve. They consider their
current state, the goal they want to reach, and plan a set of actions to get there.
They handle strategic planning and goal-oriented task execution.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
from .base import BaseConnorAgent, AgentMessage, AgentType, AgentConfig
from forge.sdk import ForgeLogger

LOG = ForgeLogger(__name__)


class GoalStatus(Enum):
    """Status of goals in the system."""
    PENDING = "pending"
    ACTIVE = "active" 
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class PlanStatus(Enum):
    """Status of execution plans."""
    DRAFT = "draft"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Goal:
    """Represents a goal in the system."""
    goal_id: str
    description: str
    priority: int = 1
    deadline: Optional[float] = None
    status: GoalStatus = GoalStatus.PENDING
    success_criteria: List[str] = None
    constraints: List[str] = None
    parent_goal_id: Optional[str] = None
    sub_goals: List[str] = None
    
    def __post_init__(self):
        if self.success_criteria is None:
            self.success_criteria = []
        if self.constraints is None:
            self.constraints = []
        if self.sub_goals is None:
            self.sub_goals = []


@dataclass
class Action:
    """Represents an action in a plan."""
    action_id: str
    description: str
    action_type: str
    parameters: Dict[str, Any] = None
    dependencies: List[str] = None
    estimated_duration: Optional[float] = None
    actual_duration: Optional[float] = None
    status: str = "pending"
    result: Optional[Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class Plan:
    """Represents an execution plan."""
    plan_id: str
    goal_id: str
    description: str
    actions: List[Action] = None
    status: PlanStatus = PlanStatus.DRAFT
    estimated_completion: Optional[float] = None
    actual_completion: Optional[float] = None
    success_probability: float = 0.5
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []


class GoalBasedAgentPlanner(BaseConnorAgent):
    """
    Goal-Based Agent-Planner that focuses on achieving specific objectives through
    strategic planning and coordinated action execution.
    
    GAPs receive processed input from MBRs and create actionable plans to achieve
    the identified goals.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.goals = {}  # goal_id -> Goal
        self.plans = {}  # plan_id -> Plan
        self.active_goals = []
        self.completed_goals = []
        self.planning_strategies = self._init_planning_strategies()
        
    def _init_planning_strategies(self) -> Dict[str, Any]:
        """Initialize planning strategies for different types of goals."""
        return {
            "information_retrieval": {
                "approach": "sequential",
                "actions": ["identify_sources", "search", "validate", "synthesize"],
                "success_factors": ["accuracy", "completeness", "timeliness"]
            },
            "task_execution": {
                "approach": "step_by_step",
                "actions": ["analyze_requirements", "break_down", "execute", "verify"],
                "success_factors": ["correctness", "efficiency", "quality"]
            },
            "problem_solving": {
                "approach": "analytical",
                "actions": ["understand_problem", "generate_solutions", "evaluate", "implement"],
                "success_factors": ["effectiveness", "creativity", "feasibility"]
            },
            "learning": {
                "approach": "iterative",
                "actions": ["gather_data", "analyze", "practice", "evaluate"],
                "success_factors": ["comprehension", "retention", "application"]
            }
        }
    
    async def process_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Process input by creating goals and plans for task execution.
        
        Args:
            input_data: Enhanced data from MBR or direct input
            
        Returns:
            Response with goals, plans, and execution strategy
        """
        # Extract input information
        if isinstance(input_data, dict):
            original_input = input_data.get("original_input", "")
            analysis = input_data.get("analysis", {})
            decision = input_data.get("decision", {})
            context = input_data.get("context", {})
        else:
            original_input = str(input_data)
            analysis = {}
            decision = {}
            context = {}
        
        # Create goal from input
        goal = self._create_goal_from_input(original_input, analysis, decision)
        
        # Generate plan for the goal
        plan = await self._generate_plan(goal, context)
        
        # Assess feasibility and adjust if needed
        feasibility = self._assess_plan_feasibility(plan, context)
        if feasibility["score"] < 0.5:
            plan = await self._revise_plan(plan, feasibility["issues"])
        
        # Create response
        response = {
            "original_input": original_input,
            "goal": self._goal_to_dict(goal),
            "plan": self._plan_to_dict(plan),
            "feasibility": feasibility,
            "processed_by": self.agent_id,
            "agent_type": self.agent_type.value,
            "execution_strategy": self._determine_execution_strategy(plan, context),
            "estimated_completion": plan.estimated_completion,
            "next_action": self._get_next_action(plan)
        }
        
        # Store goal and plan
        self.goals[goal.goal_id] = goal
        self.plans[plan.plan_id] = plan
        
        if goal.status == GoalStatus.ACTIVE:
            self.active_goals.append(goal.goal_id)
        
        # Add to memory
        self.add_to_memory({
            "goal_id": goal.goal_id,
            "plan_id": plan.plan_id,
            "goal_description": goal.description,
            "plan_description": plan.description,
            "timestamp": response.get("timestamp")
        })
        
        LOG.info(f"GAP {self.agent_id} created goal: {goal.description[:50]}...")
        
        return response
    
    def _create_goal_from_input(self, input_text: str, analysis: Dict[str, Any], 
                               decision: Dict[str, Any]) -> Goal:
        """Create a goal based on the input and analysis."""
        goal_id = str(uuid.uuid4())
        
        # Determine goal type and priority based on analysis
        intent = analysis.get("intent", "general_interaction")
        complexity = analysis.get("complexity", "medium")
        
        priority_mapping = {
            "low": 3,
            "medium": 2,
            "high": 1
        }
        
        priority = priority_mapping.get(complexity, 2)
        
        # Create goal description
        if intent == "information_seeking":
            description = f"Retrieve and provide information: {input_text}"
        elif intent == "task_execution":
            description = f"Execute task: {input_text}"
        elif intent == "goal_achievement":
            description = f"Achieve objective: {input_text}"
        else:
            description = f"Process request: {input_text}"
        
        # Define success criteria based on intent
        success_criteria = self._define_success_criteria(intent, input_text)
        
        # Create constraints based on analysis
        constraints = self._define_constraints(analysis, decision)
        
        goal = Goal(
            goal_id=goal_id,
            description=description,
            priority=priority,
            status=GoalStatus.ACTIVE,
            success_criteria=success_criteria,
            constraints=constraints
        )
        
        return goal
    
    def _define_success_criteria(self, intent: str, input_text: str) -> List[str]:
        """Define success criteria based on intent."""
        criteria_templates = {
            "information_seeking": [
                "Accurate information retrieved",
                "Comprehensive coverage of topic",
                "Information is up-to-date",
                "Sources are reliable"
            ],
            "task_execution": [
                "Task completed as specified",
                "Quality meets standards",
                "Completed within timeline",
                "No errors in execution"
            ],
            "goal_achievement": [
                "Objective fully achieved",
                "All requirements met",
                "Constraints respected",
                "Stakeholder satisfaction"
            ]
        }
        
        return criteria_templates.get(intent, [
            "Request processed successfully",
            "User satisfaction achieved",
            "No errors encountered"
        ])
    
    def _define_constraints(self, analysis: Dict[str, Any], 
                          decision: Dict[str, Any]) -> List[str]:
        """Define constraints based on analysis and decision."""
        constraints = []
        
        # Time constraints
        complexity = analysis.get("complexity", "medium")
        if complexity == "low":
            constraints.append("Complete within 5 minutes")
        elif complexity == "high":
            constraints.append("Allow sufficient time for thorough analysis")
        
        # Resource constraints
        domain = analysis.get("domain", "general")
        if domain == "technology":
            constraints.append("Use appropriate technical resources")
        elif domain == "science":
            constraints.append("Ensure scientific accuracy")
        
        # Quality constraints
        confidence = decision.get("confidence", 0.5)
        if confidence < 0.6:
            constraints.append("Verify results before finalizing")
        
        return constraints
    
    async def _generate_plan(self, goal: Goal, context: Dict[str, Any]) -> Plan:
        """Generate an execution plan for the goal."""
        plan_id = str(uuid.uuid4())
        
        # Determine planning strategy based on goal
        strategy = self._select_planning_strategy(goal)
        
        # Generate actions based on strategy
        actions = self._generate_actions(goal, strategy, context)
        
        # Estimate completion time
        estimated_completion = self._estimate_completion_time(actions)
        
        # Calculate success probability
        success_probability = self._calculate_success_probability(goal, actions, context)
        
        plan = Plan(
            plan_id=plan_id,
            goal_id=goal.goal_id,
            description=f"Plan to {goal.description}",
            actions=actions,
            status=PlanStatus.APPROVED,
            estimated_completion=estimated_completion,
            success_probability=success_probability
        )
        
        return plan
    
    def _select_planning_strategy(self, goal: Goal) -> Dict[str, Any]:
        """Select the appropriate planning strategy for the goal."""
        goal_description = goal.description.lower()
        
        if any(word in goal_description for word in ["retrieve", "find", "search", "information"]):
            return self.planning_strategies["information_retrieval"]
        elif any(word in goal_description for word in ["execute", "perform", "do", "create"]):
            return self.planning_strategies["task_execution"]
        elif any(word in goal_description for word in ["solve", "fix", "resolve", "address"]):
            return self.planning_strategies["problem_solving"]
        elif any(word in goal_description for word in ["learn", "understand", "study"]):
            return self.planning_strategies["learning"]
        else:
            return self.planning_strategies["task_execution"]  # Default
    
    def _generate_actions(self, goal: Goal, strategy: Dict[str, Any], 
                         context: Dict[str, Any]) -> List[Action]:
        """Generate specific actions based on the goal and strategy."""
        actions = []
        base_actions = strategy.get("actions", [])
        
        for i, base_action in enumerate(base_actions):
            action_id = f"{goal.goal_id}_action_{i}"
            
            # Customize action based on goal specifics
            description = self._customize_action_description(base_action, goal)
            
            # Determine action type and parameters
            action_type, parameters = self._determine_action_details(base_action, goal, context)
            
            # Set dependencies
            dependencies = [f"{goal.goal_id}_action_{i-1}"] if i > 0 else []
            
            action = Action(
                action_id=action_id,
                description=description,
                action_type=action_type,
                parameters=parameters,
                dependencies=dependencies,
                estimated_duration=self._estimate_action_duration(action_type)
            )
            
            actions.append(action)
        
        return actions
    
    def _customize_action_description(self, base_action: str, goal: Goal) -> str:
        """Customize action description based on the specific goal."""
        goal_context = goal.description.lower()
        
        customizations = {
            "identify_sources": f"Identify information sources for: {goal_context}",
            "search": f"Search for relevant information about: {goal_context}",
            "validate": f"Validate information accuracy for: {goal_context}",
            "synthesize": f"Synthesize findings for: {goal_context}",
            "analyze_requirements": f"Analyze requirements for: {goal_context}",
            "break_down": f"Break down task into steps: {goal_context}",
            "execute": f"Execute main task: {goal_context}",
            "verify": f"Verify completion of: {goal_context}",
            "understand_problem": f"Understand the problem: {goal_context}",
            "generate_solutions": f"Generate solutions for: {goal_context}",
            "evaluate": f"Evaluate options for: {goal_context}",
            "implement": f"Implement solution for: {goal_context}"
        }
        
        return customizations.get(base_action, f"{base_action.title()} for: {goal_context}")
    
    def _determine_action_details(self, base_action: str, goal: Goal, 
                                context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Determine specific action type and parameters."""
        action_mapping = {
            "identify_sources": ("research", {"sources": ["database", "web", "archive"]}),
            "search": ("information_retrieval", {"query": goal.description}),
            "validate": ("verification", {"criteria": goal.success_criteria}),
            "synthesize": ("synthesis", {"format": "comprehensive_response"}),
            "analyze_requirements": ("analysis", {"focus": "requirements"}),
            "break_down": ("decomposition", {"granularity": "step_by_step"}),
            "execute": ("execution", {"primary_task": True}),
            "verify": ("verification", {"check_criteria": goal.success_criteria}),
            "understand_problem": ("analysis", {"focus": "problem_definition"}),
            "generate_solutions": ("ideation", {"approach": "creative_analytical"}),
            "evaluate": ("evaluation", {"criteria": "feasibility_effectiveness"}),
            "implement": ("implementation", {"monitor_progress": True})
        }
        
        return action_mapping.get(base_action, ("general", {"description": base_action}))
    
    def _estimate_action_duration(self, action_type: str) -> float:
        """Estimate duration for different action types (in minutes)."""
        duration_estimates = {
            "research": 10.0,
            "information_retrieval": 5.0,
            "verification": 3.0,
            "synthesis": 8.0,
            "analysis": 15.0,
            "decomposition": 5.0,
            "execution": 20.0,
            "ideation": 12.0,
            "evaluation": 8.0,
            "implementation": 25.0,
            "general": 10.0
        }
        
        return duration_estimates.get(action_type, 10.0)
    
    def _estimate_completion_time(self, actions: List[Action]) -> float:
        """Estimate total completion time for the plan."""
        # For sequential execution, sum all durations
        total_duration = sum(action.estimated_duration or 0 for action in actions)
        
        # Add buffer for coordination and unexpected delays (20%)
        return total_duration * 1.2
    
    def _calculate_success_probability(self, goal: Goal, actions: List[Action], 
                                     context: Dict[str, Any]) -> float:
        """Calculate the probability of plan success."""
        base_probability = 0.7  # Start with optimistic base
        
        # Adjust based on goal complexity
        if goal.priority == 1:  # High priority/complexity
            base_probability -= 0.1
        elif goal.priority == 3:  # Low priority/complexity
            base_probability += 0.1
        
        # Adjust based on number of actions (more actions = more risk)
        action_penalty = min(len(actions) * 0.02, 0.2)
        base_probability -= action_penalty
        
        # Adjust based on context availability
        if context.get("relevant_entities"):
            base_probability += 0.05
        if context.get("patterns"):
            base_probability += 0.05
        
        # Adjust based on constraints
        if len(goal.constraints) > 3:
            base_probability -= 0.1
        
        return max(min(base_probability, 1.0), 0.1)  # Keep between 0.1 and 1.0
    
    def _assess_plan_feasibility(self, plan: Plan, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the feasibility of the plan."""
        issues = []
        score = 1.0
        
        # Check if plan is too long
        if plan.estimated_completion and plan.estimated_completion > 60:  # More than 1 hour
            issues.append("Plan duration may be too long")
            score -= 0.2
        
        # Check if success probability is too low
        if plan.success_probability < 0.4:
            issues.append("Success probability is low")
            score -= 0.3
        
        # Check for resource availability (simplified)
        if len(plan.actions) > 10:
            issues.append("Plan has many actions - consider simplification")
            score -= 0.1
        
        # Check for missing dependencies in context
        required_info = any("information" in action.description.lower() for action in plan.actions)
        if required_info and not context.get("relevant_entities"):
            issues.append("May need additional context for information retrieval")
            score -= 0.2
        
        return {
            "score": max(score, 0.0),
            "issues": issues,
            "recommendations": self._generate_recommendations(issues)
        }
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on identified issues."""
        recommendations = []
        
        for issue in issues:
            if "duration" in issue.lower():
                recommendations.append("Consider breaking down into smaller sub-goals")
            elif "probability" in issue.lower():
                recommendations.append("Add verification steps and fallback options")
            elif "simplification" in issue.lower():
                recommendations.append("Combine related actions or parallelize where possible")
            elif "context" in issue.lower():
                recommendations.append("Gather additional context before execution")
        
        return recommendations
    
    async def _revise_plan(self, plan: Plan, issues: List[str]) -> Plan:
        """Revise the plan to address identified issues."""
        # For now, implement simple revisions
        # In a full implementation, this would be more sophisticated
        
        if "duration" in str(issues).lower():
            # Try to parallelize some actions
            for i, action in enumerate(plan.actions[1:], 1):
                if action.action_type in ["research", "information_retrieval"]:
                    action.dependencies = []  # Remove dependency to allow parallel execution
        
        if "probability" in str(issues).lower():
            # Add verification action
            verification_action = Action(
                action_id=f"{plan.plan_id}_verification",
                description="Additional verification step",
                action_type="verification",
                parameters={"thorough_check": True},
                dependencies=[action.action_id for action in plan.actions[-2:]]
            )
            plan.actions.append(verification_action)
        
        # Recalculate estimates
        plan.estimated_completion = self._estimate_completion_time(plan.actions)
        plan.success_probability = min(plan.success_probability + 0.1, 1.0)
        
        return plan
    
    def _determine_execution_strategy(self, plan: Plan, context: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the best execution strategy for the plan."""
        strategy = {
            "approach": "sequential",
            "monitoring": "standard",
            "fallback_enabled": False,
            "parallel_actions": []
        }
        
        # Check for parallelizable actions
        parallel_candidates = []
        for action in plan.actions:
            if not action.dependencies or len(action.dependencies) == 0:
                parallel_candidates.append(action.action_id)
        
        if len(parallel_candidates) > 1:
            strategy["approach"] = "mixed"
            strategy["parallel_actions"] = parallel_candidates
        
        # Determine monitoring level
        if plan.success_probability < 0.6:
            strategy["monitoring"] = "intensive"
            strategy["fallback_enabled"] = True
        elif plan.success_probability > 0.8:
            strategy["monitoring"] = "light"
        
        return strategy
    
    def _get_next_action(self, plan: Plan) -> Optional[Dict[str, Any]]:
        """Get the next action to execute in the plan."""
        for action in plan.actions:
            if action.status == "pending":
                return {
                    "action_id": action.action_id,
                    "description": action.description,
                    "type": action.action_type,
                    "parameters": action.parameters,
                    "estimated_duration": action.estimated_duration
                }
        return None
    
    def _goal_to_dict(self, goal: Goal) -> Dict[str, Any]:
        """Convert Goal object to dictionary."""
        return {
            "goal_id": goal.goal_id,
            "description": goal.description,
            "priority": goal.priority,
            "status": goal.status.value,
            "success_criteria": goal.success_criteria,
            "constraints": goal.constraints,
            "parent_goal_id": goal.parent_goal_id,
            "sub_goals": goal.sub_goals
        }
    
    def _plan_to_dict(self, plan: Plan) -> Dict[str, Any]:
        """Convert Plan object to dictionary."""
        return {
            "plan_id": plan.plan_id,
            "goal_id": plan.goal_id,
            "description": plan.description,
            "status": plan.status.value,
            "actions": [
                {
                    "action_id": action.action_id,
                    "description": action.description,
                    "type": action.action_type,
                    "parameters": action.parameters,
                    "dependencies": action.dependencies,
                    "estimated_duration": action.estimated_duration,
                    "status": action.status
                }
                for action in plan.actions
            ],
            "estimated_completion": plan.estimated_completion,
            "success_probability": plan.success_probability
        }
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle messages from other agents."""
        if message.content.get("type") == "execute_action":
            # Execute a specific action
            action_id = message.content.get("action_id")
            result = await self._execute_action(action_id)
            
            return self.send_message(
                message.sender_id,
                message.sender_type,
                {"type": "action_result", "action_id": action_id, "result": result}
            )
        
        elif message.content.get("type") == "goal_status_update":
            # Update goal status
            goal_id = message.content.get("goal_id")
            new_status = message.content.get("status")
            
            if goal_id in self.goals:
                self.goals[goal_id].status = GoalStatus(new_status)
                LOG.info(f"Updated goal {goal_id} status to {new_status}")
        
        return None
    
    async def _execute_action(self, action_id: str) -> Dict[str, Any]:
        """Execute a specific action."""
        # Find the action in current plans
        action = None
        for plan in self.plans.values():
            for plan_action in plan.actions:
                if plan_action.action_id == action_id:
                    action = plan_action
                    break
            if action:
                break
        
        if not action:
            return {"success": False, "error": "Action not found"}
        
        # Mark action as executing
        action.status = "executing"
        
        # Simulate action execution based on type
        import time
        start_time = time.time()
        
        # Execute based on action type
        result = await self._perform_action(action)
        
        # Update action with results
        action.actual_duration = time.time() - start_time
        action.status = "completed" if result.get("success") else "failed"
        action.result = result
        
        return result
    
    async def _perform_action(self, action: Action) -> Dict[str, Any]:
        """Perform the actual action execution."""
        # This is a simplified implementation
        # In a real system, this would interface with actual execution systems
        
        action_type = action.action_type
        
        if action_type == "research":
            return {
                "success": True,
                "data": f"Research completed for: {action.description}",
                "sources_found": 5
            }
        elif action_type == "information_retrieval":
            return {
                "success": True,
                "data": f"Information retrieved for: {action.description}",
                "relevance_score": 0.85
            }
        elif action_type == "verification":
            return {
                "success": True,
                "verified": True,
                "confidence": 0.9
            }
        elif action_type == "synthesis":
            return {
                "success": True,
                "synthesis": f"Synthesized response for: {action.description}",
                "quality_score": 0.8
            }
        else:
            return {
                "success": True,
                "data": f"Action completed: {action.description}"
            }
    
    def get_planning_statistics(self) -> Dict[str, Any]:
        """Get statistics about planning performance."""
        total_goals = len(self.goals)
        completed_goals = len([g for g in self.goals.values() if g.status == GoalStatus.COMPLETED])
        active_goals = len([g for g in self.goals.values() if g.status == GoalStatus.ACTIVE])
        
        total_plans = len(self.plans)
        successful_plans = len([p for p in self.plans.values() if p.status == PlanStatus.COMPLETED])
        
        avg_success_probability = sum(p.success_probability for p in self.plans.values()) / total_plans if total_plans > 0 else 0
        
        return {
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "active_goals": active_goals,
            "goal_completion_rate": completed_goals / total_goals if total_goals > 0 else 0,
            "total_plans": total_plans,
            "successful_plans": successful_plans,
            "plan_success_rate": successful_plans / total_plans if total_plans > 0 else 0,
            "average_success_probability": avg_success_probability
        }