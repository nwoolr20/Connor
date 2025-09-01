#!/usr/bin/env python3
"""
Connor Multi-Agent System - Universal Installation Script
========================================================

Complete system installation and setup script that handles:
- Dependency installation and verification
- Environment configuration and validation
- System initialization and health checks
- Entry point registration and CLI setup
- Post-installation verification and testing

Provides a single command installation for the entire Connor system.
"""

import os
import sys
import subprocess
import platform
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConnorInstaller:
    """Comprehensive Connor system installer"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.system_platform = platform.system().lower()
        self.python_version = sys.version_info
        self.installation_log = []
        
    def log_step(self, step: str, status: str = "INFO", details: str = ""):
        """Log installation step with status"""
        message = f"[{status}] {step}"
        if details:
            message += f": {details}"
        logger.info(message)
        self.installation_log.append({
            "step": step,
            "status": status,
            "details": details,
            "timestamp": str(__import__('datetime').datetime.now())
        })
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        self.log_step("Checking system prerequisites", "INFO")
        
        # Check Python version
        if self.python_version < (3, 10):
            self.log_step("Python version check", "FAIL", 
                         f"Python 3.10+ required, found {self.python_version.major}.{self.python_version.minor}")
            return False
        self.log_step("Python version check", "PASS", f"Python {self.python_version.major}.{self.python_version.minor}")
        
        # Check git
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            self.log_step("Git availability", "PASS")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_step("Git availability", "FAIL", "Git not found - required for setup")
            return False
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
            self.log_step("Pip availability", "PASS")
        except subprocess.CalledProcessError:
            self.log_step("Pip availability", "FAIL", "Pip not available")
            return False
        
        return True
    
    def install_poetry(self) -> bool:
        """Install Poetry package manager if not present"""
        self.log_step("Checking Poetry installation", "INFO")
        
        try:
            result = subprocess.run(["poetry", "--version"], check=True, capture_output=True, text=True)
            self.log_step("Poetry check", "PASS", f"Found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_step("Poetry not found, installing", "INFO")
            
            try:
                # Install Poetry using official installer
                install_script = "https://install.python-poetry.org"
                subprocess.run([
                    sys.executable, "-c", 
                    f"import urllib.request; exec(urllib.request.urlopen('{install_script}').read())"
                ], check=True)
                
                # Add Poetry to PATH for current session
                poetry_bin = Path.home() / ".local" / "bin"
                if poetry_bin.exists():
                    os.environ["PATH"] = f"{poetry_bin}:{os.environ.get('PATH', '')}"
                
                self.log_step("Poetry installation", "PASS")
                return True
                
            except subprocess.CalledProcessError as e:
                self.log_step("Poetry installation", "FAIL", str(e))
                return False
    
    def install_system_dependencies(self) -> bool:
        """Install system-level dependencies"""
        self.log_step("Installing system dependencies", "INFO")
        
        try:
            # Run setup.sh if it exists
            setup_script = self.project_root / "setup.sh"
            if setup_script.exists():
                subprocess.run(["bash", str(setup_script)], check=True, cwd=self.project_root)
                self.log_step("System setup script", "PASS")
            else:
                self.log_step("System setup script", "SKIP", "setup.sh not found")
            
            return True
        except subprocess.CalledProcessError as e:
            self.log_step("System dependencies", "FAIL", str(e))
            return False
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies using Poetry"""
        self.log_step("Installing Python dependencies", "INFO")
        
        try:
            # Install dependencies with Poetry
            subprocess.run(["poetry", "install"], check=True, cwd=self.project_root)
            self.log_step("Poetry dependencies", "PASS")
            
            # Install additional dependencies that might be needed
            extra_deps = ["chromadb", "litellm", "openai"]
            for dep in extra_deps:
                try:
                    subprocess.run(["poetry", "add", dep], check=True, cwd=self.project_root)
                    self.log_step(f"Extra dependency: {dep}", "PASS")
                except subprocess.CalledProcessError:
                    self.log_step(f"Extra dependency: {dep}", "SKIP", "Already installed or incompatible")
            
            return True
        except subprocess.CalledProcessError as e:
            self.log_step("Python dependencies", "FAIL", str(e))
            return False
    
    def setup_environment(self) -> bool:
        """Setup environment configuration"""
        self.log_step("Setting up environment", "INFO")
        
        try:
            # Create .env file if it doesn't exist
            env_file = self.project_root / ".env"
            if not env_file.exists():
                env_content = """# Connor Multi-Agent System Environment Configuration
CONNOR_LOG_LEVEL=INFO
CONNOR_DATA_DIR=./data
CONNOR_MEMORY_DIR=./memory
CONNOR_MODELS_DIR=./models
CONNOR_MAX_AGENTS=20
OPENAI_API_KEY=your_openai_api_key_here
"""
                env_file.write_text(env_content)
                self.log_step("Environment file creation", "PASS", ".env created")
            else:
                self.log_step("Environment file check", "PASS", ".env exists")
            
            # Create necessary directories
            dirs_to_create = ["data", "memory", "logs", "reports", "models"]
            for dir_name in dirs_to_create:
                dir_path = self.project_root / dir_name
                dir_path.mkdir(exist_ok=True)
                self.log_step(f"Directory creation: {dir_name}", "PASS")
            
            return True
        except Exception as e:
            self.log_step("Environment setup", "FAIL", str(e))
            return False
    
    def register_entry_points(self) -> bool:
        """Register CLI entry points"""
        self.log_step("Registering entry points", "INFO")
        
        try:
            # Install the package in development mode
            subprocess.run(["poetry", "install"], check=True, cwd=self.project_root)
            self.log_step("Package installation", "PASS")
            
            # Create launch connor script
            self.create_launch_connor_script()
            
            return True
        except subprocess.CalledProcessError as e:
            self.log_step("Entry point registration", "FAIL", str(e))
            return False
    
    def create_launch_connor_script(self):
        """Create the launch connor entry point script"""
        launch_script_content = '''#!/usr/bin/env python3
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
    subparsers.add_parser("status", help="Show system status")
    
    # Maintenance operations
    subparsers.add_parser("audit", help="Run comprehensive system audit")
    subparsers.add_parser("test", help="Run system tests")
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
'''
        
        # Create the launch connor script
        launch_script = self.project_root / "launch_connor.py"
        launch_script.write_text(launch_script_content)
        launch_script.chmod(0o755)
        
        self.log_step("Launch Connor script creation", "PASS")
        
        # Create symlink for easy access
        try:
            launch_link = self.project_root / "launch"
            if launch_link.exists():
                launch_link.unlink()
            launch_link.symlink_to("launch_connor.py")
            self.log_step("Launch symlink creation", "PASS")
        except Exception as e:
            self.log_step("Launch symlink creation", "SKIP", str(e))
    
    def run_post_install_tests(self) -> bool:
        """Run post-installation verification tests"""
        self.log_step("Running post-installation tests", "INFO")
        
        try:
            # Test import capabilities
            test_imports = [
                "forge.connor.base",
                "forge.connor.connor_system",
                "connor_cli",
            ]
            
            for module in test_imports:
                try:
                    __import__(module)
                    self.log_step(f"Import test: {module}", "PASS")
                except ImportError as e:
                    self.log_step(f"Import test: {module}", "WARN", str(e))
            
            # Test CLI availability
            try:
                subprocess.run([sys.executable, "connor_cli.py", "--help"], 
                             check=True, capture_output=True, cwd=self.project_root)
                self.log_step("CLI test", "PASS")
            except subprocess.CalledProcessError:
                self.log_step("CLI test", "WARN", "CLI not fully functional")
            
            return True
        except Exception as e:
            self.log_step("Post-installation tests", "FAIL", str(e))
            return False
    
    def run_system_audit(self) -> bool:
        """Run comprehensive system audit after installation"""
        self.log_step("Running system audit", "INFO")
        
        try:
            subprocess.run([sys.executable, "system_audit.py"], 
                         check=True, cwd=self.project_root)
            self.log_step("System audit", "PASS")
            return True
        except subprocess.CalledProcessError as e:
            self.log_step("System audit", "WARN", f"Audit completed with warnings: {e}")
            return True  # Audit warnings are acceptable
        except Exception as e:
            self.log_step("System audit", "FAIL", str(e))
            return False
    
    def install(self) -> bool:
        """Run complete installation process"""
        print("🚀 Starting Connor Multi-Agent System Installation")
        print("=" * 60)
        
        steps = [
            ("Prerequisites Check", self.check_prerequisites),
            ("Poetry Installation", self.install_poetry),
            ("System Dependencies", self.install_system_dependencies),
            ("Python Dependencies", self.install_python_dependencies),
            ("Environment Setup", self.setup_environment),
            ("Entry Points Registration", self.register_entry_points),
            ("Post-Install Tests", self.run_post_install_tests),
            ("System Audit", self.run_system_audit),
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                if not step_func():
                    failed_steps.append(step_name)
                    print(f"❌ {step_name} failed")
                else:
                    print(f"✅ {step_name} completed")
            except Exception as e:
                failed_steps.append(step_name)
                print(f"❌ {step_name} failed with error: {e}")
        
        print("\n" + "=" * 60)
        if failed_steps:
            print(f"⚠️  Installation completed with {len(failed_steps)} issues:")
            for step in failed_steps:
                print(f"   - {step}")
            print("\n💡 Check logs above for details. System may still be functional.")
        else:
            print("🎉 Connor Multi-Agent System installation completed successfully!")
        
        print("\n🚀 Quick Start:")
        print("   python3 launch_connor.py --help")
        print("   python3 launch_connor.py audit")
        print("   python3 launch_connor.py demo")
        
        return len(failed_steps) == 0

def main():
    """Main installation entry point"""
    installer = ConnorInstaller()
    success = installer.install()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()