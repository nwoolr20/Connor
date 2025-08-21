"""Integration tests for CLI functionality."""

import pytest
import subprocess
import sys


def test_connor_cli_help():
    """Test that connor --help works and shows expected content."""
    try:
        # Just test the console script directly
        result = subprocess.run(["connor", "--help"], 
                              capture_output=True, 
                              text=True,
                              timeout=30)
        
        assert result.returncode == 0
        output = result.stdout.lower()
        assert "usage:" in output
        assert "commands:" in output
        assert "agent" in output  # Should show agent commands
        
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        pytest.fail(f"connor --help failed: {e}")


def test_connor_cli_console_script():
    """Test that connor console script is available."""
    try:
        result = subprocess.run(["connor", "--help"], 
                              capture_output=True, 
                              text=True,
                              timeout=30)
        assert result.returncode == 0
    except FileNotFoundError:
        pytest.fail("connor console script not found - check packaging")
    except subprocess.TimeoutExpired:
        pytest.fail("connor console script timed out")


def test_connor_cli_automation_console_script():
    """Test that connor-cli console script is available."""
    try:
        result = subprocess.run(["connor-cli", "--help"], 
                              capture_output=True, 
                              text=True,
                              timeout=30)
        assert result.returncode == 0
        output = result.stdout.lower()
        assert "connor system automation cli" in output
        assert "start" in output  # Should show start command
        
    except FileNotFoundError:
        pytest.fail("connor-cli console script not found - check packaging")
    except subprocess.TimeoutExpired:
        pytest.fail("connor-cli console script timed out")


def test_python_cli_equivalence():
    """Test that python cli.py and connor console script work similarly."""
    try:
        # Test main CLI
        result1 = subprocess.run(["python", "cli.py", "--help"], 
                               capture_output=True, 
                               text=True,
                               timeout=30)
        result2 = subprocess.run(["connor", "--help"], 
                               capture_output=True, 
                               text=True,
                               timeout=30)
        
        assert result1.returncode == 0
        assert result2.returncode == 0
        
        # Both should show similar command structure
        assert "agent" in result1.stdout.lower()
        assert "agent" in result2.stdout.lower()
        
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        pytest.fail(f"CLI equivalence test failed: {e}")


def test_connor_agent_start_help():
    """Test that connor agent start shows Connor as an option."""
    try:
        # This tests that the CLI modification to handle connor agent works
        result = subprocess.run(["connor", "agent", "--help"], 
                              capture_output=True, 
                              text=True,
                              timeout=30)
        
        assert result.returncode == 0
        output = result.stdout
        assert "start" in output.lower()
        
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        pytest.fail(f"connor agent commands test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])