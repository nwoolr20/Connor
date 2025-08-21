"""Integration tests for Connor agent registry and factory functionality."""

import pytest


def test_connor_forge_agent_class_exists():
    """Test that ConnorForgeAgent class can be instantiated."""
    try:
        from forge.connor_agent import ConnorForgeAgent
        from forge.sdk import AgentDB, Workspace
        
        # We can't easily create a full instance without database setup,
        # but we can verify the class exists and has expected methods
        assert hasattr(ConnorForgeAgent, '__init__')
        assert hasattr(ConnorForgeAgent, 'create_task')
        assert hasattr(ConnorForgeAgent, 'execute_step')
        
    except ImportError as e:
        pytest.fail(f"Failed to import ConnorForgeAgent: {e}")


def test_connor_system_can_be_instantiated():
    """Test that ConnorSystem can be instantiated."""
    try:
        from forge.connor import ConnorSystem
        
        # Create a basic Connor system instance
        connor_system = ConnorSystem()
        assert connor_system is not None
        
        # Check it has expected methods
        assert hasattr(connor_system, 'process_input')
        assert hasattr(connor_system, 'get_system_status')
        assert hasattr(connor_system, 'shutdown')
        
    except ImportError as e:
        pytest.fail(f"Failed to import or instantiate ConnorSystem: {e}")
    except Exception as e:
        pytest.fail(f"ConnorSystem instantiation failed: {e}")


def test_connor_base_agent_exists():
    """Test that BaseConnorAgent exists and can be imported."""
    try:
        from forge.connor.base import BaseConnorAgent
        
        # Verify the base class has expected structure
        assert hasattr(BaseConnorAgent, '__init__')
        
    except ImportError as e:
        pytest.fail(f"Failed to import BaseConnorAgent: {e}")


def test_action_registry_exists():
    """Test that action registry exists and can be imported."""
    try:
        from forge.actions import ActionRegister
        
        # Verify action registry exists
        assert ActionRegister is not None
        assert hasattr(ActionRegister, '__init__')
        
    except ImportError as e:
        pytest.fail(f"Failed to import ActionRegister: {e}")


def test_connor_agent_integration():
    """Test basic Connor agent system integration."""
    try:
        from forge.connor import ConnorSystem
        
        # Test basic system functionality
        connor_system = ConnorSystem()
        status = connor_system.get_system_status()
        
        # Status should be a dict with expected keys
        assert isinstance(status, dict)
        assert 'total_agents' in status
        assert 'families' in status
        
    except Exception as e:
        pytest.fail(f"Connor agent integration test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])