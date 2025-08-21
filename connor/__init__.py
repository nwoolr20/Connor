"""
Connor Multi-Agent System

A comprehensive agent-based AI system with integration capabilities.
"""

__version__ = "1.0.0"
__author__ = "Connor Development Team"

# Make key components available at package level
try:
    from autogpts.forge.forge.connor_agent import ConnorForgeAgent
    from autogpts.forge.forge.connor.base import BaseConnorAgent
    
    __all__ = ["ConnorForgeAgent", "BaseConnorAgent"]
except ImportError:
    # Graceful degradation if forge modules aren't available
    __all__ = []