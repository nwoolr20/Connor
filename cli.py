#!/usr/bin/env python3
"""
Connor System CLI Interface
==========================

Main command-line interface for the Connor Multi-Agent System.
Provides unified access to all Connor functionality including:
- System management and monitoring
- Agent operations and control
- Configuration management
- Development and debugging tools
"""

import click
import asyncio
import sys
import os
from pathlib import Path

# Add Connor modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autogpts', 'forge'))

@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    """Connor Multi-Agent System CLI"""
    ctx.ensure_object(dict)

@cli.command()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
def start(config, debug):
    """Start the Connor system"""
    click.echo("🚀 Starting Connor Multi-Agent System...")
    
    try:
        from forge.connor.connor_system import ConnorSystem
        
        if debug:
            click.echo("Debug mode enabled")
            
        connor = ConnorSystem()
        
        status = connor.get_system_status()
        click.echo(f"✅ Connor system started successfully")
        click.echo(f"📊 System status: {status}")
        
    except Exception as e:
        click.echo(f"❌ Failed to start Connor system: {e}", err=True)
        sys.exit(1)

@cli.command()
def status():
    """Check Connor system status"""
    click.echo("📊 Checking Connor system status...")
    
    try:
        from forge.connor.connor_system import ConnorSystem
        connor = ConnorSystem()
        status = connor.get_system_status()
        
        click.echo(f"✅ System Status: {status}")
        
        if hasattr(connor, 'agents'):
            agent_count = len(connor.agents)
            click.echo(f"🤖 Active Agents: {agent_count}")
            
            for agent_id, agent in connor.agents.items():
                click.echo(f"  - {agent_id}: {agent.agent_type.value}")
                
    except Exception as e:
        click.echo(f"❌ Failed to get system status: {e}", err=True)
        sys.exit(1)

@cli.command()
def agents():
    """List and manage agents"""
    click.echo("🤖 Connor Agents:")
    
    try:
        from forge.connor.connor_system import ConnorSystem
        connor = ConnorSystem()
        
        if hasattr(connor, 'agents') and connor.agents:
            for agent_id, agent in connor.agents.items():
                click.echo(f"  • {agent_id}")
                click.echo(f"    Type: {agent.agent_type.value}")
                click.echo(f"    Phase: {getattr(agent, 'phase', 'N/A')}")
                click.echo("")
        else:
            click.echo("  No agents currently active")
            
    except Exception as e:
        click.echo(f"❌ Failed to list agents: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--output', '-o', default='connor_audit_report.json', help='Output file path')
def audit():
    """Run comprehensive system audit"""
    click.echo("🔍 Running Connor system audit...")
    
    try:
        from system_audit import ConnorSystemAuditor
        
        async def run_audit():
            auditor = ConnorSystemAuditor()
            await auditor.run_full_audit()
            
        asyncio.run(run_audit())
        click.echo("✅ Audit completed successfully")
        
    except Exception as e:
        click.echo(f"❌ Audit failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('query')
@click.option('--agent-type', help='Specific agent type to use')
def query(query, agent_type):
    """Send a query to the Connor system"""
    click.echo(f"💭 Processing query: {query}")
    
    try:
        from forge.connor.connor_system import ConnorSystem
        connor = ConnorSystem()
        
        # Simple query processing example
        if hasattr(connor, 'agents') and connor.agents:
            first_agent = next(iter(connor.agents.values()))
            click.echo(f"🤖 Routing to agent: {first_agent.agent_type.value}")
            click.echo("📝 Query processed (basic implementation)")
        else:
            click.echo("❌ No agents available to process query")
            
    except Exception as e:
        click.echo(f"❌ Query processing failed: {e}", err=True)
        sys.exit(1)

@cli.command()
def config():
    """Show configuration information"""
    click.echo("⚙️ Connor Configuration:")
    
    config_files = [
        'connor_config.json',
        '.env',
        'pyproject.toml'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            click.echo(f"  ✅ {config_file}")
        else:
            click.echo(f"  ❌ {config_file} (missing)")

@cli.command()
def version():
    """Show version information"""
    click.echo("🔹 Connor Multi-Agent System v1.0.0")
    click.echo("🔹 Python CLI Interface")
    click.echo("🔹 Built with Click framework")

if __name__ == '__main__':
    cli()