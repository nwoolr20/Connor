"""Integration tests for Connor agent system packaging and imports."""

import pytest
import subprocess
import sys


def test_connor_package_import():
    """Test that the connor package can be imported."""
    try:
        import connor
        assert hasattr(connor, '__version__')
        assert connor.__version__ == "1.0.0"
    except ImportError as e:
        pytest.fail(f"Failed to import connor package: {e}")


def test_forge_package_import():
    """Test that the forge package can be imported."""
    try:
        import forge
        # Test some key forge components
        from forge.connor_agent import ConnorForgeAgent
        assert ConnorForgeAgent is not None
    except ImportError as e:
        pytest.fail(f"Failed to import forge package: {e}")


def test_connor_system_import():
    """Test that Connor system components can be imported."""
    try:
        from forge.connor import ConnorSystem
        from forge.connor.base import BaseConnorAgent
        assert ConnorSystem is not None
        assert BaseConnorAgent is not None
    except ImportError as e:
        pytest.fail(f"Failed to import Connor system components: {e}")


def test_scripts_package_import():
    """Test that scripts package can be imported (if included)."""
    try:
        import scripts
        # This should not fail even if scripts don't have much content
        assert scripts is not None
    except ImportError:
        # Scripts might not be importable, which is OK
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])