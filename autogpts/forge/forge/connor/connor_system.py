"""
Connor System

The main orchestrator for the Connor multi-agent system that coordinates
all six agent types and manages the forefront process flow.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
import time
import uuid
from .base import BaseConnorAgent, AgentMessage, AgentType, AgentConfig, AgentPhase
from .sra import SimpleReflexAgent
from .mbr import ModelBasedReflexAgent
from .gap import GoalBasedAgentPlanner
from .la import LearningAgent
from .uba import UtilityBasedAgent
from .aa import ApprenticeAgent
from forge.sdk import ForgeLogger

LOG = ForgeLogger(__name__)


@dataclass
class ProcessingRequest:
    """Represents a request flowing through the Connor system."""
    request_id: str
    original_input: str
    current_stage: str
    processing_history: List[Dict[str, Any]]
    priority: int = 3
    deadline: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    total_requests_processed: int = 0
    average_processing_time: float = 0.0
    success_rate: float = 1.0
    agent_utilization: Dict[str, float] = None
    bottlenecks: List[str] = None
    
    def __post_init__(self):
        if self.agent_utilization is None:
            self.agent_utilization = {}
        if self.bottlenecks is None:
            self.bottlenecks = []


class ConnorSystem:
    """
    The main Connor system that orchestrates all agent types and manages
    the forefront process: SRA → MBR → GAP with LA monitoring and UBA optimization.
    """
    
    def __init__(self, system_config: Dict[str, Any] = None):
        self.system_id = str(uuid.uuid4())
        self.config = system_config or {}
        
        # Initialize agents
        self.agents = {}
        self.agent_pools = {
            AgentType.SRA: [],
            AgentType.MBR: [],
            AgentType.GAP: [],
            AgentType.LA: [],
            AgentType.UBA: [],
            AgentType.AA: []
        }
        
        # System state
        self.active_requests = {}
        self.completed_requests = []
        self.processing_queue = asyncio.Queue()
        self.system_metrics = SystemMetrics()
        self.family_registry = {}  # Track learning agent families
        
        # Initialize default agents
        self._initialize_default_agents()
        
        LOG.info(f"Connor System {self.system_id} initialized with {sum(len(pool) for pool in self.agent_pools.values())} agents")
    
    def _initialize_default_agents(self) -> None:
        """Initialize default set of agents for the system."""
        # Create SRAs (3 for load balancing)
        for i in range(3):
            sra_config = AgentConfig(
                agent_id=f"sra_{i}",
                agent_type=AgentType.SRA,
                max_memory_size=500
            )
            sra = SimpleReflexAgent(sra_config)
            self.agents[sra.agent_id] = sra
            self.agent_pools[AgentType.SRA].append(sra.agent_id)
        
        # Create MBRs (2 for context processing)
        for i in range(2):
            mbr_config = AgentConfig(
                agent_id=f"mbr_{i}",
                agent_type=AgentType.MBR,
                max_memory_size=1000
            )
            mbr = ModelBasedReflexAgent(mbr_config)
            self.agents[mbr.agent_id] = mbr
            self.agent_pools[AgentType.MBR].append(mbr.agent_id)
        
        # Create GAPs (2 for planning)
        for i in range(2):
            gap_config = AgentConfig(
                agent_id=f"gap_{i}",
                agent_type=AgentType.GAP,
                max_memory_size=800
            )
            gap = GoalBasedAgentPlanner(gap_config)
            self.agents[gap.agent_id] = gap
            self.agent_pools[AgentType.GAP].append(gap.agent_id)
        
        # Create initial Learning Agent family
        family_id = "family_0"
        
        # Parent LA
        parent_la_config = AgentConfig(
            agent_id="la_parent_0",
            agent_type=AgentType.LA,
            phase=AgentPhase.PARENT,
            family_id=family_id,
            max_memory_size=1500
        )
        parent_la = LearningAgent(parent_la_config)
        self.agents[parent_la.agent_id] = parent_la
        self.agent_pools[AgentType.LA].append(parent_la.agent_id)
        
        # Child LAs
        for i in range(3):
            child_config = AgentConfig(
                agent_id=f"la_child_{i}",
                agent_type=AgentType.LA,
                phase=AgentPhase.CHILD,
                family_id=family_id,
                parent_id=parent_la.agent_id,
                max_memory_size=800
            )
            child_la = LearningAgent(child_config)
            self.agents[child_la.agent_id] = child_la
            self.agent_pools[AgentType.LA].append(child_la.agent_id)
        
        # Create Apprentice Agent (since family has >2 children)
        aa_config = AgentConfig(
            agent_id="aa_0",
            agent_type=AgentType.AA,
            family_id=family_id,
            parent_id=parent_la.agent_id,
            max_memory_size=1200
        )
        aa = ApprenticeAgent(aa_config)
        self.agents[aa.agent_id] = aa
        self.agent_pools[AgentType.AA].append(aa.agent_id)
        
        # Register family
        self.family_registry[family_id] = {
            "parent": parent_la.agent_id,
            "children": [f"la_child_{i}" for i in range(3)],
            "apprentices": [aa.agent_id],
            "creation_time": time.time()
        }
        
        # Create UBA for optimization
        uba_config = AgentConfig(
            agent_id="uba_0",
            agent_type=AgentType.UBA,
            max_memory_size=1000
        )
        uba = UtilityBasedAgent(uba_config)
        self.agents[uba.agent_id] = uba
        self.agent_pools[AgentType.UBA].append(uba.agent_id)
    
    async def process_input(self, user_input: str, priority: int = 3, 
                          metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user input through the Connor system forefront process.
        
        Args:
            user_input: The user's input to process
            priority: Priority level (1=high, 5=low)
            metadata: Additional metadata about the request
            
        Returns:
            Final response from the system
        """
        request_id = f"req_{int(time.time())}_{len(self.active_requests)}"
        
        # Create processing request
        request = ProcessingRequest(
            request_id=request_id,
            original_input=user_input,
            current_stage="sra",
            processing_history=[],
            priority=priority,
            metadata=metadata or {}
        )
        
        self.active_requests[request_id] = request
        
        try:
            # Execute forefront process: SRA → MBR → GAP
            final_response = await self._execute_forefront_process(request)
            
            # Move to completed requests
            self.completed_requests.append(request)
            if request_id in self.active_requests:
                del self.active_requests[request_id]
            
            # Update system metrics
            self._update_system_metrics(request, success=True)
            
            LOG.info(f"Connor System completed request {request_id}")
            
            return final_response
            
        except Exception as e:
            LOG.error(f"Error processing request {request_id}: {e}")
            
            # Update metrics for failure
            self._update_system_metrics(request, success=False)
            
            # Move to completed with error
            request.metadata["error"] = str(e)
            self.completed_requests.append(request)
            if request_id in self.active_requests:
                del self.active_requests[request_id]
            
            return {
                "request_id": request_id,
                "success": False,
                "error": str(e),
                "original_input": user_input
            }
    
    async def _execute_forefront_process(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Execute the main forefront process: SRA → MBR → GAP."""
        start_time = time.time()
        
        # Stage 1: Simple Reflex Agent processing
        sra_result = await self._process_with_sra(request)
        
        # Stage 2: Model-Based Reflex Agent processing
        mbr_result = await self._process_with_mbr(request, sra_result)
        
        # Stage 3: Goal-Based Agent-Planner processing
        gap_result = await self._process_with_gap(request, mbr_result)
        
        # Parallel: Learning Agent monitoring and analysis
        la_analysis = await self._monitor_with_las(request, [sra_result, mbr_result, gap_result])
        
        # Optimization: Utility-Based Agent evaluation
        uba_optimization = await self._optimize_with_uba(request, gap_result, la_analysis)
        
        # Final synthesis
        final_response = await self._synthesize_final_response(
            request, sra_result, mbr_result, gap_result, la_analysis, uba_optimization
        )
        
        processing_time = time.time() - start_time
        final_response["processing_time"] = processing_time
        final_response["request_id"] = request.request_id
        
        return final_response
    
    async def _process_with_sra(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process input with Simple Reflex Agent."""
        # Select least busy SRA
        sra_id = self._select_agent(AgentType.SRA)
        sra = self.agents[sra_id]
        
        request.current_stage = "sra"
        
        # Process with SRA
        sra_result = await sra.process_input(request.original_input)
        
        # Record processing history
        request.processing_history.append({
            "stage": "sra",
            "agent_id": sra_id,
            "timestamp": time.time(),
            "result": sra_result
        })
        
        LOG.debug(f"SRA {sra_id} processed request {request.request_id}")
        
        return sra_result
    
    async def _process_with_mbr(self, request: ProcessingRequest, sra_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process SRA output with Model-Based Reflex Agent."""
        # Select appropriate MBR based on complexity or load balance
        mbr_id = self._select_agent(AgentType.MBR, criteria={"complexity": sra_result.get("tags", [])})
        mbr = self.agents[mbr_id]
        
        request.current_stage = "mbr"
        
        # Enhance SRA result with original input information
        mbr_input = sra_result.copy()
        mbr_input["original_input"] = request.original_input
        
        # Process with MBR
        mbr_result = await mbr.process_input(mbr_input)
        
        # Record processing history
        request.processing_history.append({
            "stage": "mbr",
            "agent_id": mbr_id,
            "timestamp": time.time(),
            "result": mbr_result
        })
        
        LOG.debug(f"MBR {mbr_id} processed request {request.request_id}")
        
        return mbr_result
    
    async def _process_with_gap(self, request: ProcessingRequest, mbr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process MBR output with Goal-Based Agent-Planner."""
        # Select GAP based on goal complexity or current load
        gap_id = self._select_agent(AgentType.GAP, criteria={"decision_complexity": mbr_result.get("decision", {})})
        gap = self.agents[gap_id]
        
        request.current_stage = "gap"
        
        # Process with GAP
        gap_result = await gap.process_input(mbr_result)
        
        # Record processing history
        request.processing_history.append({
            "stage": "gap",
            "agent_id": gap_id,
            "timestamp": time.time(),
            "result": gap_result
        })
        
        LOG.debug(f"GAP {gap_id} processed request {request.request_id}")
        
        return gap_result
    
    async def _monitor_with_las(self, request: ProcessingRequest, 
                              stage_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Monitor processing with Learning Agents (parallel to main flow)."""
        # Select diverse LAs for monitoring
        monitoring_las = self._select_multiple_agents(AgentType.LA, count=2)
        
        monitoring_results = []
        
        for la_id in monitoring_las:
            la = self.agents[la_id]
            
            # Create monitoring input combining all stage results
            monitoring_input = {
                "original_input": request.original_input,
                "sra_result": stage_results[0] if len(stage_results) > 0 else {},
                "mbr_result": stage_results[1] if len(stage_results) > 1 else {},
                "gap_result": stage_results[2] if len(stage_results) > 2 else {},
                "monitoring_mode": True
            }
            
            # Process with LA
            la_result = await la.process_input(monitoring_input)
            monitoring_results.append({
                "agent_id": la_id,
                "phase": la.phase.value,
                "analysis": la_result
            })
        
        # Synthesize monitoring insights
        monitoring_synthesis = self._synthesize_la_monitoring(monitoring_results)
        
        LOG.debug(f"LA monitoring completed for request {request.request_id}")
        
        return monitoring_synthesis
    
    async def _optimize_with_uba(self, request: ProcessingRequest, 
                               gap_result: Dict[str, Any],
                               la_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize final decision with Utility-Based Agent."""
        # Select UBA for optimization
        uba_id = self._select_agent(AgentType.UBA)
        uba = self.agents[uba_id]
        
        # Create optimization input
        optimization_input = {
            "original_input": request.original_input,
            "gap_result": gap_result,
            "la_insights": la_analysis,
            "optimization_mode": True,
            "priority": request.priority
        }
        
        # Process with UBA
        uba_result = await uba.process_input(optimization_input)
        
        LOG.debug(f"UBA {uba_id} optimized request {request.request_id}")
        
        return uba_result
    
    def _select_agent(self, agent_type: AgentType, criteria: Dict[str, Any] = None) -> str:
        """Select the best agent of given type based on criteria."""
        available_agents = self.agent_pools[agent_type]
        
        if not available_agents:
            raise ValueError(f"No agents available of type {agent_type}")
        
        if len(available_agents) == 1:
            return available_agents[0]
        
        # Simple load balancing - select agent with shortest memory
        # In a real system, this would be more sophisticated
        best_agent_id = available_agents[0]
        min_load = len(self.agents[best_agent_id].memory)
        
        for agent_id in available_agents[1:]:
            agent_load = len(self.agents[agent_id].memory)
            if agent_load < min_load:
                min_load = agent_load
                best_agent_id = agent_id
        
        return best_agent_id
    
    def _select_multiple_agents(self, agent_type: AgentType, count: int) -> List[str]:
        """Select multiple agents of given type for parallel processing."""
        available_agents = self.agent_pools[agent_type]
        
        if not available_agents:
            return []
        
        # Return up to 'count' agents, prioritizing different phases for LAs
        if agent_type == AgentType.LA:
            # Try to get agents from different phases
            phase_agents = {}
            for agent_id in available_agents:
                agent = self.agents[agent_id]
                phase = agent.phase
                if phase not in phase_agents:
                    phase_agents[phase] = []
                phase_agents[phase].append(agent_id)
            
            selected = []
            for phase_list in phase_agents.values():
                if len(selected) < count:
                    selected.extend(phase_list[:count - len(selected)])
            
            return selected[:count]
        else:
            return available_agents[:count]
    
    def _synthesize_la_monitoring(self, monitoring_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize insights from Learning Agent monitoring."""
        if not monitoring_results:
            return {"monitoring_available": False}
        
        synthesis = {
            "monitoring_available": True,
            "agents_consulted": len(monitoring_results),
            "phase_distribution": {},
            "common_insights": [],
            "learning_recommendations": [],
            "confidence_levels": []
        }
        
        # Analyze phase distribution
        for result in monitoring_results:
            phase = result["phase"]
            synthesis["phase_distribution"][phase] = synthesis["phase_distribution"].get(phase, 0) + 1
            
            # Extract insights
            analysis = result["analysis"]
            insights = analysis.get("learned_insights", {})
            
            # Collect confidence levels
            confidence = analysis.get("confidence", 0.5)
            synthesis["confidence_levels"].append(confidence)
            
            # Collect recommendations
            recommendations = insights.get("recommendations", [])
            synthesis["learning_recommendations"].extend(recommendations)
        
        # Calculate average confidence
        if synthesis["confidence_levels"]:
            synthesis["average_confidence"] = sum(synthesis["confidence_levels"]) / len(synthesis["confidence_levels"])
        else:
            synthesis["average_confidence"] = 0.5
        
        # Remove duplicate recommendations
        synthesis["learning_recommendations"] = list(set(synthesis["learning_recommendations"]))
        
        return synthesis
    
    async def _synthesize_final_response(self, request: ProcessingRequest,
                                       sra_result: Dict[str, Any],
                                       mbr_result: Dict[str, Any],
                                       gap_result: Dict[str, Any],
                                       la_analysis: Dict[str, Any],
                                       uba_optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize final response from all processing stages."""
        final_response = {
            "original_input": request.original_input,
            "request_id": request.request_id,
            "success": True,
            "processing_stages": {
                "sra": {
                    "classification": sra_result.get("input_type"),
                    "tags": sra_result.get("tags", []),
                    "quick_response": sra_result.get("quick_response")
                },
                "mbr": {
                    "confidence": mbr_result.get("confidence"),
                    "context_applied": len(mbr_result.get("context", {}).get("relevant_entities", [])),
                    "decision": mbr_result.get("decision", {}).get("action")
                },
                "gap": {
                    "goal_created": gap_result.get("goal", {}).get("description"),
                    "plan_steps": len(gap_result.get("plan", {}).get("actions", [])),
                    "estimated_completion": gap_result.get("estimated_completion")
                },
                "la_monitoring": {
                    "agents_consulted": la_analysis.get("agents_consulted", 0),
                    "average_confidence": la_analysis.get("average_confidence", 0.5),
                    "recommendations": la_analysis.get("learning_recommendations", [])
                },
                "uba_optimization": {
                    "alternatives_considered": uba_optimization.get("alternatives_considered", 0),
                    "selected_alternative": uba_optimization.get("selected_alternative"),
                    "expected_utility": uba_optimization.get("expected_utility", 0.0)
                }
            },
            "final_answer": self._generate_final_answer(sra_result, mbr_result, gap_result, la_analysis, uba_optimization),
            "system_confidence": self._calculate_system_confidence(sra_result, mbr_result, gap_result, la_analysis, uba_optimization),
            "next_steps": gap_result.get("next_action"),
            "learning_applied": la_analysis.get("monitoring_available", False),
            "optimization_applied": uba_optimization.get("optimization_applied", False)
        }
        
        return final_response
    
    def _generate_final_answer(self, sra_result: Dict[str, Any],
                             mbr_result: Dict[str, Any],
                             gap_result: Dict[str, Any],
                             la_analysis: Dict[str, Any],
                             uba_optimization: Dict[str, Any]) -> str:
        """Generate the final answer for the user."""
        # Start with SRA quick response
        base_response = sra_result.get("quick_response", "Processing your request...")
        
        # Enhance with MBR context if available
        decision = mbr_result.get("decision", {})
        if decision.get("confidence", 0) > 0.7:
            base_response += f" Based on contextual analysis, I'll {decision.get('action', 'proceed')}."
        
        # Add GAP goal and plan information
        goal = gap_result.get("goal", {})
        if goal:
            base_response += f" I've created a plan to {goal.get('description', 'address your request')}."
            
            next_action = gap_result.get("next_action")
            if next_action:
                base_response += f" The next step is: {next_action.get('description', 'proceeding with execution')}."
        
        # Add learning insights if available
        if la_analysis.get("learning_recommendations"):
            recommendations = la_analysis["learning_recommendations"][:2]  # Top 2
            if recommendations:
                base_response += f" Based on learned patterns, I recommend: {', '.join(recommendations)}."
        
        # Add optimization results
        if uba_optimization.get("selected_alternative"):
            base_response += f" I've optimized the approach using {uba_optimization['selected_alternative']}."
        
        return base_response
    
    def _calculate_system_confidence(self, sra_result: Dict[str, Any],
                                   mbr_result: Dict[str, Any],
                                   gap_result: Dict[str, Any],
                                   la_analysis: Dict[str, Any],
                                   uba_optimization: Dict[str, Any]) -> float:
        """Calculate overall system confidence in the response."""
        confidences = []
        
        # MBR confidence
        mbr_confidence = mbr_result.get("confidence", 0.5)
        confidences.append(mbr_confidence)
        
        # GAP plan confidence
        gap_confidence = gap_result.get("feasibility", {}).get("score", 0.5)
        confidences.append(gap_confidence)
        
        # LA monitoring confidence
        la_confidence = la_analysis.get("average_confidence", 0.5)
        confidences.append(la_confidence)
        
        # UBA optimization confidence
        uba_confidence = uba_optimization.get("confidence", 0.5)
        confidences.append(uba_confidence)
        
        # Calculate weighted average (more weight to later stages)
        weights = [0.2, 0.3, 0.25, 0.25]
        weighted_confidence = sum(c * w for c, w in zip(confidences, weights))
        
        return min(max(weighted_confidence, 0.0), 1.0)
    
    def _update_system_metrics(self, request: ProcessingRequest, success: bool) -> None:
        """Update system-wide performance metrics."""
        self.system_metrics.total_requests_processed += 1
        
        # Update success rate
        total_requests = self.system_metrics.total_requests_processed
        current_successes = (self.system_metrics.success_rate * (total_requests - 1)) + (1 if success else 0)
        self.system_metrics.success_rate = current_successes / total_requests
        
        # Update average processing time
        if success and request.processing_history:
            start_time = request.processing_history[0]["timestamp"]
            end_time = request.processing_history[-1]["timestamp"]
            processing_time = end_time - start_time
            
            current_avg = self.system_metrics.average_processing_time
            self.system_metrics.average_processing_time = (
                (current_avg * (total_requests - 1)) + processing_time
            ) / total_requests
    
    async def create_learning_agent_family(self, parent_phase: AgentPhase = AgentPhase.PARENT) -> str:
        """Create a new learning agent family."""
        family_id = f"family_{len(self.family_registry)}"
        
        # Create parent LA
        parent_config = AgentConfig(
            agent_id=f"la_parent_{family_id}",
            agent_type=AgentType.LA,
            phase=parent_phase,
            family_id=family_id,
            max_memory_size=1500
        )
        parent_la = LearningAgent(parent_config)
        self.agents[parent_la.agent_id] = parent_la
        self.agent_pools[AgentType.LA].append(parent_la.agent_id)
        
        # Register family
        self.family_registry[family_id] = {
            "parent": parent_la.agent_id,
            "children": [],
            "apprentices": [],
            "creation_time": time.time()
        }
        
        LOG.info(f"Created new learning agent family: {family_id}")
        
        return family_id
    
    async def expand_family(self, family_id: str, num_children: int = 2) -> List[str]:
        """Expand a learning agent family with children."""
        if family_id not in self.family_registry:
            raise ValueError(f"Family {family_id} not found")
        
        family = self.family_registry[family_id]
        parent_id = family["parent"]
        parent_agent = self.agents[parent_id]
        
        created_children = []
        
        for i in range(num_children):
            child_config = AgentConfig(
                agent_id=f"la_child_{family_id}_{len(family['children']) + i}",
                agent_type=AgentType.LA,
                phase=AgentPhase.CHILD,
                family_id=family_id,
                parent_id=parent_id,
                max_memory_size=800
            )
            
            # Use parent's create_child_agent method if available
            if hasattr(parent_agent, 'create_child_agent'):
                child_la = parent_agent.create_child_agent(child_config)
            else:
                child_la = LearningAgent(child_config)
            
            self.agents[child_la.agent_id] = child_la
            self.agent_pools[AgentType.LA].append(child_la.agent_id)
            family["children"].append(child_la.agent_id)
            created_children.append(child_la.agent_id)
        
        # Create apprentice agent if family has >2 children
        total_children = len(family["children"])
        if total_children > 2 and not family["apprentices"]:
            aa_config = AgentConfig(
                agent_id=f"aa_{family_id}",
                agent_type=AgentType.AA,
                family_id=family_id,
                parent_id=parent_id,
                max_memory_size=1200
            )
            aa = ApprenticeAgent(aa_config)
            self.agents[aa.agent_id] = aa
            self.agent_pools[AgentType.AA].append(aa.agent_id)
            family["apprentices"].append(aa.agent_id)
            
            LOG.info(f"Created apprentice agent {aa.agent_id} for family {family_id}")
        
        LOG.info(f"Expanded family {family_id} with {num_children} children")
        
        return created_children
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        agent_counts = {agent_type.value: len(pool) for agent_type, pool in self.agent_pools.items()}
        
        return {
            "system_id": self.system_id,
            "total_agents": sum(agent_counts.values()),
            "agent_distribution": agent_counts,
            "active_requests": len(self.active_requests),
            "completed_requests": len(self.completed_requests),
            "families": len(self.family_registry),
            "system_metrics": {
                "total_processed": self.system_metrics.total_requests_processed,
                "success_rate": self.system_metrics.success_rate,
                "avg_processing_time": self.system_metrics.average_processing_time
            },
            "family_details": {
                fid: {
                    "parent": family["parent"],
                    "children_count": len(family["children"]),
                    "apprentices_count": len(family["apprentices"])
                }
                for fid, family in self.family_registry.items()
            }
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the Connor system."""
        LOG.info(f"Shutting down Connor System {self.system_id}")
        
        # Wait for active requests to complete (with timeout)
        shutdown_timeout = 30  # seconds
        start_time = time.time()
        
        while self.active_requests and (time.time() - start_time) < shutdown_timeout:
            await asyncio.sleep(1)
        
        # Force cleanup remaining requests
        for request_id in list(self.active_requests.keys()):
            request = self.active_requests[request_id]
            request.metadata["force_shutdown"] = True
            self.completed_requests.append(request)
            del self.active_requests[request_id]
        
        LOG.info(f"Connor System {self.system_id} shutdown complete")
    
    def __repr__(self):
        return f"ConnorSystem(id={self.system_id}, agents={sum(len(pool) for pool in self.agent_pools.values())}, families={len(self.family_registry)})"