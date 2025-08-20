"""
Connor Forge Agent

Integrates the Connor multi-agent system with the AutoGPT Forge framework.
This agent serves as the main interface between users and the Connor system.
"""

import asyncio
import json
from typing import Any, Dict
from forge.actions import ActionRegister
from forge.agent import ForgeAgent
from forge.sdk import (
    Agent,
    AgentDB,
    ForgeLogger,
    Step,
    StepRequestBody,
    Task,
    TaskRequestBody,
    Workspace,
)
from .connor_system import ConnorSystem

LOG = ForgeLogger(__name__)


class ConnorForgeAgent(ForgeAgent):
    """
    Connor Forge Agent that integrates the Connor multi-agent system
    with the AutoGPT Forge framework.
    
    This agent acts as the interface between users and the Connor system,
    handling task creation and step execution through the Connor agents.
    """
    
    def __init__(self, database: AgentDB, workspace: Workspace):
        """
        Initialize the Connor Forge Agent.
        
        Args:
            database: The agent database for storing tasks and steps
            workspace: The workspace for file operations
        """
        super().__init__(database, workspace)
        
        # Initialize Connor system
        self.connor_system = ConnorSystem()
        
        # Track Connor tasks
        self.connor_tasks = {}  # task_id -> connor_request_id
        
        LOG.info("Connor Forge Agent initialized with Connor multi-agent system")
    
    async def create_task(self, task_request: TaskRequestBody) -> Task:
        """
        Create a task for the Connor system.
        
        Args:
            task_request: The task request from the user
            
        Returns:
            Created task object
        """
        task = await super().create_task(task_request)
        
        LOG.info(
            f"📦 Connor Task created: {task.task_id} input: {task.input[:40]}{'...' if len(task.input) > 40 else ''}"
        )
        
        return task
    
    async def execute_step(self, task_id: str, step_request: StepRequestBody) -> Step:
        """
        Execute a step using the Connor multi-agent system.
        
        Args:
            task_id: ID of the task being executed
            step_request: The step request body
            
        Returns:
            Completed step object
        """
        # Get the task
        task = await self.db.get_task(task_id)
        
        # Create step
        step = await self.db.create_step(
            task_id=task_id, 
            input=step_request, 
            is_last=False  # We'll determine this based on Connor's response
        )
        
        try:
            # Determine input for Connor system
            if task_id not in self.connor_tasks:
                # First step - use task input
                connor_input = task.input
                priority = self._determine_priority(task.input, step_request.input)
            else:
                # Subsequent step - use step input
                connor_input = step_request.input
                priority = 3  # Default priority for follow-up steps
            
            # Process with Connor system
            LOG.info(f"🤖 Processing with Connor system: {connor_input[:50]}...")
            
            connor_response = await self.connor_system.process_input(
                user_input=connor_input,
                priority=priority,
                metadata={
                    "task_id": task_id,
                    "step_id": step.step_id,
                    "forge_agent": True
                }
            )
            
            # Store Connor request mapping
            if "request_id" in connor_response:
                self.connor_tasks[task_id] = connor_response["request_id"]
            
            # Process Connor response
            step_output = self._process_connor_response(connor_response, task, step)
            
            # Create artifacts if any files were created
            artifacts_created = await self._create_artifacts_from_response(
                connor_response, task_id, step.step_id
            )
            
            # Update step with output
            step.output = step_output
            
            # Determine if this should be the last step
            is_last = self._should_be_last_step(connor_response, step_request)
            step.is_last = is_last
            
            LOG.info(
                f"✅ Connor Step completed: {step.step_id}\n"
                f"Connor system processed request with confidence: {connor_response.get('system_confidence', 0.5):.2f}\n"
                f"Artifacts created: {len(artifacts_created)}\n"
                f"Is last step: {is_last}"
            )
            
        except Exception as e:
            LOG.error(f"Error in Connor step execution: {e}")
            step.output = f"Error processing with Connor system: {str(e)}"
            step.is_last = True
        
        return step
    
    def _determine_priority(self, task_input: str, step_input: str) -> int:
        """
        Determine priority level for Connor processing.
        
        Args:
            task_input: The original task input
            step_input: The current step input
            
        Returns:
            Priority level (1=urgent, 5=low)
        """
        # Check for urgent keywords
        urgent_keywords = ["urgent", "emergency", "critical", "asap", "immediate"]
        high_keywords = ["important", "priority", "needed", "required"]
        
        combined_input = f"{task_input} {step_input}".lower()
        
        if any(keyword in combined_input for keyword in urgent_keywords):
            return 1  # Urgent
        elif any(keyword in combined_input for keyword in high_keywords):
            return 2  # High
        elif len(combined_input) > 200:
            return 2  # High priority for complex requests
        else:
            return 3  # Normal
    
    def _process_connor_response(self, connor_response: Dict[str, Any], 
                               task: Task, step: Step) -> str:
        """
        Process Connor system response into step output.
        
        Args:
            connor_response: Response from Connor system
            task: Current task object
            step: Current step object
            
        Returns:
            Formatted step output
        """
        if not connor_response.get("success", True):
            return f"Connor system encountered an error: {connor_response.get('error', 'Unknown error')}"
        
        # Extract key information from Connor response
        final_answer = connor_response.get("final_answer", "Processing completed.")
        confidence = connor_response.get("system_confidence", 0.5)
        next_steps = connor_response.get("next_steps")
        
        # Build comprehensive output
        output_parts = [
            f"🤖 **Connor Multi-Agent System Response**",
            f"",
            f"**Answer:** {final_answer}",
            f"",
            f"**System Confidence:** {confidence:.1%}",
        ]
        
        # Add processing stage information
        stages = connor_response.get("processing_stages", {})
        if stages:
            output_parts.extend([
                f"",
                f"**Processing Pipeline:**"
            ])
            
            # SRA results
            sra = stages.get("sra", {})
            if sra:
                output_parts.append(f"• **Simple Reflex Agent:** Classified as '{sra.get('classification')}' with tags: {', '.join(sra.get('tags', []))}")
            
            # MBR results
            mbr = stages.get("mbr", {})
            if mbr:
                output_parts.append(f"• **Model-Based Agent:** Applied context analysis (confidence: {mbr.get('confidence', 0.5):.1%})")
            
            # GAP results
            gap = stages.get("gap", {})
            if gap:
                goal_desc = gap.get("goal_created", "")
                if goal_desc:
                    output_parts.append(f"• **Goal Planner:** Created plan - {goal_desc[:80]}{'...' if len(goal_desc) > 80 else ''}")
            
            # LA monitoring
            la = stages.get("la_monitoring", {})
            if la and la.get("agents_consulted", 0) > 0:
                output_parts.append(f"• **Learning Agents:** {la.get('agents_consulted')} agents provided insights")
            
            # UBA optimization
            uba = stages.get("uba_optimization", {})
            if uba and uba.get("alternatives_considered", 0) > 0:
                output_parts.append(f"• **Utility Optimizer:** Evaluated {uba.get('alternatives_considered')} alternatives")
        
        # Add next steps if available
        if next_steps:
            output_parts.extend([
                f"",
                f"**Next Step:** {next_steps.get('description', 'Continue with plan execution')}"
            ])
        
        # Add processing metrics
        processing_time = connor_response.get("processing_time")
        if processing_time:
            output_parts.extend([
                f"",
                f"**Processing Time:** {processing_time:.2f} seconds"
            ])
        
        return "\n".join(output_parts)
    
    async def _create_artifacts_from_response(self, connor_response: Dict[str, Any],
                                            task_id: str, step_id: str) -> List[str]:
        """
        Create artifacts based on Connor response.
        
        Args:
            connor_response: Response from Connor system
            task_id: Current task ID
            step_id: Current step ID
            
        Returns:
            List of created artifact file names
        """
        artifacts_created = []
        
        try:
            # Create a detailed response file
            response_filename = f"connor_response_{step_id}.json"
            response_data = {
                "connor_response": connor_response,
                "timestamp": connor_response.get("processing_time"),
                "system_confidence": connor_response.get("system_confidence"),
                "processing_stages": connor_response.get("processing_stages", {})
            }
            
            # Write response data to workspace
            response_json = json.dumps(response_data, indent=2, default=str)
            self.workspace.write(
                task_id=task_id,
                path=response_filename,
                data=response_json.encode('utf-8')
            )
            
            # Create artifact record
            await self.db.create_artifact(
                task_id=task_id,
                step_id=step_id,
                file_name=response_filename,
                relative_path="",
                agent_created=True,
            )
            
            artifacts_created.append(response_filename)
            
            # Create a human-readable summary
            summary_filename = f"connor_summary_{step_id}.md"
            summary_content = self._create_summary_content(connor_response)
            
            self.workspace.write(
                task_id=task_id,
                path=summary_filename,
                data=summary_content.encode('utf-8')
            )
            
            await self.db.create_artifact(
                task_id=task_id,
                step_id=step_id,
                file_name=summary_filename,
                relative_path="",
                agent_created=True,
            )
            
            artifacts_created.append(summary_filename)
            
        except Exception as e:
            LOG.warning(f"Failed to create Connor artifacts: {e}")
        
        return artifacts_created
    
    def _create_summary_content(self, connor_response: Dict[str, Any]) -> str:
        """
        Create a human-readable summary of Connor's response.
        
        Args:
            connor_response: Response from Connor system
            
        Returns:
            Markdown formatted summary
        """
        summary_lines = [
            "# Connor Multi-Agent System - Processing Summary",
            "",
            f"**Request ID:** {connor_response.get('request_id', 'N/A')}",
            f"**Original Input:** {connor_response.get('original_input', 'N/A')}",
            f"**System Confidence:** {connor_response.get('system_confidence', 0.5):.1%}",
            f"**Processing Time:** {connor_response.get('processing_time', 0):.2f} seconds",
            "",
            "## Final Answer",
            "",
            connor_response.get('final_answer', 'No answer provided'),
            "",
            "## Processing Pipeline",
            ""
        ]
        
        stages = connor_response.get("processing_stages", {})
        
        # SRA stage
        sra = stages.get("sra", {})
        if sra:
            summary_lines.extend([
                "### Simple Reflex Agent (SRA)",
                f"- **Classification:** {sra.get('classification', 'N/A')}",
                f"- **Tags:** {', '.join(sra.get('tags', []))}",
                f"- **Quick Response:** {sra.get('quick_response', 'N/A')}",
                ""
            ])
        
        # MBR stage
        mbr = stages.get("mbr", {})
        if mbr:
            summary_lines.extend([
                "### Model-Based Reflex Agent (MBR)",
                f"- **Confidence:** {mbr.get('confidence', 0.5):.1%}",
                f"- **Context Entities:** {mbr.get('context_applied', 0)}",
                f"- **Decision:** {mbr.get('decision', 'N/A')}",
                ""
            ])
        
        # GAP stage
        gap = stages.get("gap", {})
        if gap:
            summary_lines.extend([
                "### Goal-Based Agent-Planner (GAP)",
                f"- **Goal:** {gap.get('goal_created', 'N/A')}",
                f"- **Plan Steps:** {gap.get('plan_steps', 0)}",
                f"- **Estimated Completion:** {gap.get('estimated_completion', 'N/A')} minutes",
                ""
            ])
        
        # LA monitoring
        la = stages.get("la_monitoring", {})
        if la and la.get("agents_consulted", 0) > 0:
            summary_lines.extend([
                "### Learning Agent (LA) Monitoring",
                f"- **Agents Consulted:** {la.get('agents_consulted', 0)}",
                f"- **Average Confidence:** {la.get('average_confidence', 0.5):.1%}",
                f"- **Recommendations:** {len(la.get('recommendations', []))}",
                ""
            ])
        
        # UBA optimization
        uba = stages.get("uba_optimization", {})
        if uba and uba.get("alternatives_considered", 0) > 0:
            summary_lines.extend([
                "### Utility-Based Agent (UBA) Optimization",
                f"- **Alternatives Considered:** {uba.get('alternatives_considered', 0)}",
                f"- **Selected Alternative:** {uba.get('selected_alternative', 'N/A')}",
                f"- **Expected Utility:** {uba.get('expected_utility', 0.0):.3f}",
                ""
            ])
        
        # Next steps
        next_steps = connor_response.get('next_steps')
        if next_steps:
            summary_lines.extend([
                "## Next Steps",
                "",
                next_steps.get('description', 'Continue with execution'),
                ""
            ])
        
        return "\n".join(summary_lines)
    
    def _should_be_last_step(self, connor_response: Dict[str, Any], 
                           step_request: StepRequestBody) -> bool:
        """
        Determine if this should be the last step based on Connor's response.
        
        Args:
            connor_response: Response from Connor system
            step_request: Current step request
            
        Returns:
            True if this should be the last step
        """
        # Check if Connor indicates completion
        final_answer = connor_response.get("final_answer", "")
        
        # Keywords that suggest completion
        completion_keywords = [
            "completed", "finished", "done", "accomplished", 
            "achieved", "resolved", "answered", "provided"
        ]
        
        # Check if the final answer suggests completion
        if any(keyword in final_answer.lower() for keyword in completion_keywords):
            return True
        
        # Check if user input suggests they want to continue
        user_input = step_request.input.lower()
        continue_keywords = ["continue", "next", "more", "keep going", "proceed"]
        
        if any(keyword in user_input for keyword in continue_keywords):
            return False
        
        # Check system confidence - high confidence might indicate completion
        confidence = connor_response.get("system_confidence", 0.5)
        if confidence > 0.8 and not connor_response.get("next_steps"):
            return True
        
        # Default to not last step to allow for follow-up
        return False
    
    async def get_connor_system_status(self) -> Dict[str, Any]:
        """Get the status of the Connor system."""
        return self.connor_system.get_system_status()
    
    async def shutdown(self) -> None:
        """Shutdown the Connor Forge Agent."""
        LOG.info("Shutting down Connor Forge Agent...")
        
        # Shutdown Connor system
        if hasattr(self, 'connor_system'):
            await self.connor_system.shutdown()
        
        LOG.info("Connor Forge Agent shutdown complete")
    
    def __repr__(self):
        return f"ConnorForgeAgent(connor_system={self.connor_system})"