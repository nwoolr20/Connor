"""
Connor-AutoGPT Integration Agent

This agent replaces AutoGPT's single agent decision-making with Connor's
sophisticated multi-agent system while preserving AutoGPT's proven interface.
"""

import asyncio
import logging
from typing import Any, Dict, Optional, Tuple

from autogpt.agents.agent import Agent, AgentConfiguration, AgentSettings
from autogpt.core.resource.model_providers import ChatModelProvider
from autogpt.file_storage.base import FileStorage
from autogpt.models.action_history import ActionResult, ActionSuccessResult, ActionErrorResult
from autogpt.models.command_registry import CommandRegistry
from autogpt.config import Config

# Import Connor system
import sys
import os
# Add the forge path to sys.path to import Connor
forge_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'forge'))
if forge_path not in sys.path:
    sys.path.insert(0, forge_path)

try:
    from forge.connor.connor_system import ConnorSystem
    CONNOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Connor system not available: {e}")
    CONNOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConnorAgent(Agent):
    """
    An AutoGPT Agent powered by Connor's multi-agent system.
    
    This agent maintains AutoGPT's interface while using Connor's
    sophisticated multi-agent decision-making pipeline under the hood.
    """
    
    def __init__(
        self,
        settings: AgentSettings,
        llm_provider: ChatModelProvider,
        command_registry: CommandRegistry,
        file_storage: FileStorage,
        legacy_config: Config,
    ):
        super().__init__(
            settings=settings,
            llm_provider=llm_provider,
            command_registry=command_registry,
            file_storage=file_storage,
            legacy_config=legacy_config,
        )
        
        # Initialize Connor system
        self.connor_system = None
        if CONNOR_AVAILABLE:
            try:
                self.connor_system = ConnorSystem()
                logger.info("Connor multi-agent system initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Connor system: {e}")
        else:
            logger.warning("Connor system not available, falling back to standard AutoGPT agent")
    
    async def propose_action(self) -> Tuple[str, dict, str]:
        """
        Propose the next action using Connor's multi-agent system.
        
        This replaces AutoGPT's single-agent decision making with Connor's
        sophisticated multi-agent pipeline (SRA → MBR → GAP → LA → UBA → AA).
        """
        if not self.connor_system:
            # Fallback to parent behavior if Connor system unavailable
            return await super().propose_action()
        
        try:
            # Get current context and task
            context = self._build_context_for_connor()
            
            # Process through Connor's multi-agent system
            connor_response = await self.connor_system.process_input(
                user_input=context,
                priority=3,
                metadata={"agent_id": self.state.agent_id, "cycle": self.config.cycle_count}
            )
            
            # Extract command and arguments from Connor's response
            command_name, arguments, assistant_reply = self._parse_connor_response(connor_response)
            
            logger.info(f"Connor system proposed action: {command_name} with args: {arguments}")
            return command_name, arguments, assistant_reply
            
        except Exception as e:
            logger.error(f"Error in Connor system decision-making: {e}")
            # Fallback to parent behavior on error
            return await super().propose_action()
    
    def _build_context_for_connor(self) -> str:
        """
        Build context string for Connor's multi-agent system.
        
        Combines the agent's task, current state, and recent history
        into a comprehensive context for Connor to analyze.
        """
        context_parts = [
            f"Task: {self.state.task}",
            f"Agent Name: {self.state.ai_profile.ai_name}",
            f"Agent Role: {self.state.ai_profile.ai_role}",
            f"Cycle Count: {self.config.cycle_count}",
        ]
        
        # Add recent action history
        if hasattr(self.state, 'history') and self.state.history:
            recent_actions = self.state.history.get_last_n_cycles(3)
            if recent_actions:
                context_parts.append("Recent Actions:")
                for i, action in enumerate(recent_actions, 1):
                    context_parts.append(f"  {i}. {action.action.name}: {action.action.args}")
                    if action.result:
                        context_parts.append(f"     Result: {action.result}")
        
        # Add current goals/constraints
        if self.state.directives:
            if self.state.directives.constraints:
                context_parts.append("Constraints:")
                for constraint in self.state.directives.constraints:
                    context_parts.append(f"  - {constraint}")
            
            if self.state.directives.resources:
                context_parts.append("Available Resources:")
                for resource in self.state.directives.resources:
                    context_parts.append(f"  - {resource}")
        
        return "\n".join(context_parts)
    
    def _parse_connor_response(self, connor_response: Dict[str, Any]) -> Tuple[str, dict, str]:
        """
        Parse Connor's comprehensive response into AutoGPT command format.
        
        Connor returns rich analysis with recommended actions. This method
        extracts the specific command and arguments AutoGPT expects.
        """
        try:
            # Extract the recommended action from Connor's response
            final_response = connor_response.get('final_response', {})
            recommended_action = final_response.get('recommended_action', 'think')
            
            # Default to 'think' command with Connor's analysis
            command_name = "think"
            arguments = {
                "thoughts": {
                    "text": final_response.get('summary', 'Connor analysis completed'),
                    "reasoning": final_response.get('reasoning', 'Multi-agent analysis'),
                    "plan": final_response.get('plan', 'Continue with task'),
                    "criticism": final_response.get('considerations', 'Reviewed by Connor system')
                }
            }
            
            # Try to extract more specific action if Connor recommends one
            if 'action_type' in final_response:
                action_type = final_response['action_type']
                
                if action_type == 'command_execution':
                    command_name = final_response.get('command', 'think')
                    if 'command_args' in final_response:
                        arguments.update(final_response['command_args'])
                
                elif action_type == 'file_operation':
                    if 'file_path' in final_response:
                        command_name = "read_file"
                        arguments["filename"] = final_response['file_path']
                
                elif action_type == 'search':
                    command_name = "web_search"
                    arguments["query"] = final_response.get('search_query', 'research task')
                
                elif action_type == 'finish':
                    command_name = "finish"
                    arguments["reason"] = final_response.get('summary', 'Task completed by Connor system')
            
            # Create assistant reply with Connor's full analysis
            assistant_reply = self._format_connor_analysis(connor_response)
            
            return command_name, arguments, assistant_reply
            
        except Exception as e:
            logger.error(f"Error parsing Connor response: {e}")
            # Safe fallback
            return "think", {
                "thoughts": {
                    "text": "Connor system analysis completed",
                    "reasoning": "Multi-agent processing pipeline executed",
                    "plan": "Continue with next steps",
                    "criticism": "Need to review Connor integration"
                }
            }, "Connor multi-agent system has analyzed the situation."
    
    def _format_connor_analysis(self, connor_response: Dict[str, Any]) -> str:
        """
        Format Connor's comprehensive analysis for user display.
        
        Presents Connor's multi-agent insights in a clear, structured format.
        """
        try:
            lines = ["🤖 Connor Multi-Agent Analysis:", ""]
            
            # System metrics
            if 'system_metrics' in connor_response:
                metrics = connor_response['system_metrics']
                lines.append(f"📊 System Status: {metrics.get('success_rate', 1.0)*100:.1f}% success rate")
                lines.append("")
            
            # Agent contributions
            if 'agent_insights' in connor_response:
                insights = connor_response['agent_insights']
                lines.append("🧠 Agent Insights:")
                
                for agent_type, insight in insights.items():
                    if insight and insight.get('recommendation'):
                        lines.append(f"  • {agent_type}: {insight['recommendation']}")
                lines.append("")
            
            # Final recommendation
            final_response = connor_response.get('final_response', {})
            if final_response:
                lines.append("🎯 Final Recommendation:")
                lines.append(f"  {final_response.get('summary', 'Analysis complete')}")
                
                if 'reasoning' in final_response:
                    lines.append("")
                    lines.append("💭 Reasoning:")
                    lines.append(f"  {final_response['reasoning']}")
                
                if 'next_steps' in final_response:
                    lines.append("")
                    lines.append("📋 Next Steps:")
                    for step in final_response['next_steps']:
                        lines.append(f"  • {step}")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting Connor analysis: {e}")
            return "Connor multi-agent system has completed its analysis."