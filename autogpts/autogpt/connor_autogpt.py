#!/usr/bin/env python3
"""
Connor-AutoGPT Main Entry Point

This is the primary entry point for the integrated Connor-AutoGPT system.
It replaces the standard AutoGPT entry with Connor's multi-agent intelligence
while preserving all of AutoGPT's proven interface and functionality.
"""

import os
import sys

# Ensure proper path configuration for Connor integration
project_root = os.path.dirname(os.path.abspath(__file__))
forge_path = os.path.join(os.path.dirname(project_root), 'forge')

# Add forge to Python path for Connor system
if os.path.exists(forge_path):
    sys.path.insert(0, forge_path)

# Add current directory for AutoGPT modules
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Main entry point for Connor-AutoGPT integrated system."""
    try:
        # Import Connor system to verify availability
        from forge.connor.connor_system import ConnorSystem
        print("🤖 Connor-AutoGPT Integrated System")
        print("   Multi-Agent Intelligence + Proven Interface")
        print()
        
        # Import and run AutoGPT CLI with Connor integration
        import autogpt.app.cli
        autogpt.app.cli.cli()
        
    except ImportError as e:
        print(f"❌ Connor system not available: {e}")
        print("   Falling back to standard AutoGPT...")
        print()
        
        # Fallback to standard AutoGPT if Connor unavailable
        import autogpt.app.cli
        autogpt.app.cli.cli()
    
    except Exception as e:
        print(f"❌ Error starting Connor-AutoGPT: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()