#!/usr/bin/env python3
"""
Connor System Automation CLI
Provides command-line interface for all Connor automation features.
"""

import asyncio
import argparse
import sys
import subprocess
from pathlib import Path

class ConnorAutomationCLI:
    def __init__(self):
        self.project_root = Path("/home/runner/work/Connor/Connor")
        
    async def setup_system(self, args):
        """Setup the Connor system."""
        print("🚀 Setting up Connor system...")
        subprocess.run(["make", "setup"], cwd=self.project_root, check=True)
        
    async def run_tests(self, args):
        """Run tests."""
        test_type = args.type or "all"
        
        if test_type == "all":
            subprocess.run(["make", "test"], cwd=self.project_root, check=True)
        elif test_type == "unit":
            subprocess.run(["make", "test-unit"], cwd=self.project_root, check=True)
        elif test_type == "integration":
            subprocess.run(["make", "test-integration"], cwd=self.project_root, check=True)
        elif test_type == "performance":
            subprocess.run(["make", "test-performance"], cwd=self.project_root, check=True)
        else:
            print(f"Unknown test type: {test_type}")
            sys.exit(1)
    
    async def health_check(self, args):
        """Run health check."""
        if args.continuous:
            subprocess.run([
                "python", "scripts/monitor.py", 
                "--interval", str(args.interval)
            ], cwd=self.project_root)
        else:
            subprocess.run([
                "python", "scripts/monitor.py", "--one-shot"
            ], cwd=self.project_root, check=True)
    
    async def deploy_system(self, args):
        """Deploy the system."""
        cmd = ["python", "scripts/deploy.py", "--env", args.environment]
        if args.rollback:
            cmd.append("--rollback")
        
        subprocess.run(cmd, cwd=self.project_root, check=True)
    
    async def auto_update(self, args):
        """Run auto-update."""
        cmd = ["python", "scripts/auto_update.py"]
        if args.dry_run:
            cmd.append("--dry-run")
        if args.force:
            cmd.append("--force")
        if args.backup_only:
            cmd.append("--backup-only")
        
        subprocess.run(cmd, cwd=self.project_root, check=True)
    
    async def run_demo(self, args):
        """Run Connor demo."""
        if args.automated:
            subprocess.run(["make", "demo-automated"], cwd=self.project_root, check=True)
        else:
            subprocess.run(["make", "demo"], cwd=self.project_root, check=True)
    
    async def quality_check(self, args):
        """Run code quality checks."""
        if args.format:
            subprocess.run(["make", "format"], cwd=self.project_root, check=True)
        
        subprocess.run(["make", "lint"], cwd=self.project_root, check=True)
        
        if args.security:
            subprocess.run(["make", "security"], cwd=self.project_root, check=True)
    
    async def system_start(self, args):
        """Start Connor system."""
        subprocess.run(["make", "start"], cwd=self.project_root, check=True)
    
    async def system_stop(self, args):
        """Stop Connor system."""
        subprocess.run(["make", "stop"], cwd=self.project_root, check=True)
    
    async def system_restart(self, args):
        """Restart Connor system."""
        subprocess.run(["make", "restart"], cwd=self.project_root, check=True)
    
    async def cleanup(self, args):
        """Clean up system."""
        subprocess.run(["make", "clean"], cwd=self.project_root, check=True)
        
        if args.deep:
            subprocess.run(["make", "clean-deep"], cwd=self.project_root)
    
    async def backup_system(self, args):
        """Create system backup."""
        subprocess.run(["make", "backup"], cwd=self.project_root, check=True)
    
    async def full_cycle(self, args):
        """Run full development cycle."""
        subprocess.run(["make", "full-cycle"], cwd=self.project_root, check=True)

def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Connor System Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s setup                     # Setup Connor system
  %(prog)s test --type unit          # Run unit tests
  %(prog)s health --continuous       # Run continuous health monitoring
  %(prog)s deploy --env production   # Deploy to production
  %(prog)s update --dry-run          # Check for updates without applying
  %(prog)s demo --automated          # Run automated demo
  %(prog)s quality --format          # Format code and run quality checks
  %(prog)s full-cycle                # Run complete development cycle
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup Connor system')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--type', choices=['unit', 'integration', 'performance', 'all'],
                           help='Type of tests to run (default: all)')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check system health')
    health_parser.add_argument('--continuous', action='store_true', 
                             help='Run continuous monitoring')
    health_parser.add_argument('--interval', type=int, default=30,
                             help='Monitoring interval in seconds (default: 30)')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy system')
    deploy_parser.add_argument('--env', dest='environment', 
                             choices=['local', 'dev', 'staging', 'production'],
                             default='local', help='Target environment')
    deploy_parser.add_argument('--rollback', action='store_true',
                             help='Rollback deployment')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Auto-update system')
    update_parser.add_argument('--dry-run', action='store_true',
                             help='Show what would be updated')
    update_parser.add_argument('--force', action='store_true',
                             help='Force update even if up to date')
    update_parser.add_argument('--backup-only', action='store_true',
                             help='Create backup only')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run Connor demo')
    demo_parser.add_argument('--automated', action='store_true',
                           help='Run automated demo')
    
    # Quality command
    quality_parser = subparsers.add_parser('quality', help='Run code quality checks')
    quality_parser.add_argument('--format', action='store_true',
                               help='Format code before checking')
    quality_parser.add_argument('--security', action='store_true',
                               help='Include security scans')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start Connor system')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop Connor system')
    
    # Restart command
    restart_parser = subparsers.add_parser('restart', help='Restart Connor system')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up system')
    cleanup_parser.add_argument('--deep', action='store_true',
                               help='Deep cleanup including caches')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create system backup')
    
    # Full cycle command
    cycle_parser = subparsers.add_parser('full-cycle', help='Run full development cycle')
    
    return parser

async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ConnorAutomationCLI()
    
    # Map commands to methods
    command_map = {
        'setup': cli.setup_system,
        'test': cli.run_tests,
        'health': cli.health_check,
        'deploy': cli.deploy_system,
        'update': cli.auto_update,
        'demo': cli.run_demo,
        'quality': cli.quality_check,
        'start': cli.system_start,
        'stop': cli.system_stop,
        'restart': cli.system_restart,
        'cleanup': cli.cleanup,
        'backup': cli.backup_system,
        'full-cycle': cli.full_cycle
    }
    
    if args.command in command_map:
        try:
            await command_map[args.command](args)
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed with exit code {e.returncode}")
            sys.exit(e.returncode)
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            sys.exit(1)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())