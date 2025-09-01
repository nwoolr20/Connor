#!/usr/bin/env python3
"""
Connor Multi-Agent System - Launch Command
==========================================

Single entry point for the Connor Multi-Agent System.
Provides unified access to all system components and operations.
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add Connor modules to path
sys.path.insert(0, str(Path(__file__).parent / "autogpts" / "forge"))

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        prog="launch connor",
        description="Connor Multi-Agent System - Unified Entry Point"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # System operations
    subparsers.add_parser("start", help="Start Connor system")
    subparsers.add_parser("stop", help="Stop Connor system")
    subparsers.add_parser("restart", help="Restart Connor system")
    
    # Status with optional continuous flag
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.add_argument("--continuous", action="store_true", help="Continuous monitoring")
    
    # Maintenance operations
    subparsers.add_parser("audit", help="Run comprehensive system audit")
    
    # Test with optional type
    test_parser = subparsers.add_parser("test", help="Run system tests")
    test_parser.add_argument("--type", choices=["all", "unit", "integration", "performance"], 
                           default="all", help="Test type to run")
    
    subparsers.add_parser("setup", help="Setup/reinstall system")
    subparsers.add_parser("health", help="Health check")
    
    # Interactive operations
    subparsers.add_parser("demo", help="Run interactive demo")
    subparsers.add_parser("chat", help="Start chat interface")
    
    return parser

async def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Import Connor CLI after path setup
    from connor_cli import ConnorAutomationCLI
    
    cli = ConnorAutomationCLI()
    
    # Map commands to CLI methods
    command_map = {
        "start": cli.system_start,
        "stop": cli.system_stop,
        "restart": cli.system_restart,
        "status": cli.health_check,
        "audit": lambda _: run_audit(),
        "test": cli.run_tests,
        "setup": cli.setup_system,
        "health": cli.health_check,
        "demo": cli.run_demo,
        "chat": lambda _: start_chat()
    }
    
    if args.command in command_map:
        try:
            await command_map[args.command](args)
        except Exception as e:
            print(f"❌ Error executing {args.command}: {e}")
            sys.exit(1)
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

async def run_audit():
    """Run comprehensive system audit"""
    print("🔍 Starting Connor System Comprehensive Audit...")
    from system_audit import ConnorSystemAuditor
    auditor = ConnorSystemAuditor()
    await auditor.run_full_audit()

async def start_chat():
    """Start interactive chat interface"""
    print("💬 Starting Connor Chat Interface...")
    from demo_connor import main as demo_main
    await demo_main()

if __name__ == "__main__":
    asyncio.run(main())
