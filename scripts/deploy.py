#!/usr/bin/env python3
"""
Connor System Deployment Automation
Handles automated deployment, configuration, and environment setup.
"""

import asyncio
import subprocess
import sys
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class ConnorDeployment:
    def __init__(self, target_env="local"):
        self.target_env = target_env
        self.project_root = Path("/home/runner/work/Connor/Connor")
        self.forge_path = self.project_root / "autogpts" / "forge"
        self.config = {}
        
    async def deploy(self):
        """Run complete deployment process."""
        print("🚀 Starting Connor System Deployment")
        print("=" * 50)
        
        try:
            await self.pre_deployment_checks()
            await self.setup_environment()
            await self.install_dependencies()
            await self.configure_system()
            await self.run_tests()
            await self.post_deployment_setup()
            
            print("\n" + "=" * 50)
            print("✅ Connor System Deployment Complete!")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            await self.rollback()
            raise

    async def pre_deployment_checks(self):
        """Run pre-deployment checks."""
        print("\n🔍 Running pre-deployment checks...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            raise Exception(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check available disk space
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (1024**3)
        if free_gb < 2:
            raise Exception(f"Insufficient disk space: {free_gb}GB available, 2GB required")
        print(f"✅ Disk space: {free_gb}GB available")
        
        # Check Git status
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  cwd=self.project_root, capture_output=True, text=True)
            if result.stdout.strip():
                print("⚠️  Uncommitted changes detected")
            else:
                print("✅ Git repository clean")
        except Exception:
            print("⚠️  Git not available or not a git repository")

    async def setup_environment(self):
        """Setup deployment environment."""
        print("\n🔧 Setting up environment...")
        
        # Create necessary directories
        directories = [
            self.project_root / "logs",
            self.project_root / "reports",
            self.project_root / "reports" / "tests",
            self.project_root / "reports" / "coverage",
            self.project_root / "reports" / "security",
            self.project_root / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory.name}")
        
        # Setup environment file
        env_template = self.forge_path / ".env.example"
        env_file = self.forge_path / ".env"
        
        if env_template.exists() and not env_file.exists():
            shutil.copy(env_template, env_file)
            print("✅ Created .env from template")
        
        # Set default environment variables
        env_vars = {
            "CONNOR_ENV": self.target_env,
            "CONNOR_LOG_LEVEL": "INFO",
            "CONNOR_MONITOR_INTERVAL": "30"
        }
        
        for key, value in env_vars.items():
            if key not in os.environ:
                os.environ[key] = value
                print(f"✅ Set environment variable: {key}={value}")

    async def install_dependencies(self):
        """Install system and Python dependencies."""
        print("\n📦 Installing dependencies...")
        
        # Check for Poetry
        try:
            result = subprocess.run(["poetry", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Poetry available: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📥 Installing Poetry...")
            # Use setup.sh if available
            setup_script = self.project_root / "setup.sh"
            if setup_script.exists():
                subprocess.run([str(setup_script)], check=True)
            else:
                raise Exception("Poetry not found and setup.sh not available")
        
        # Install Python dependencies
        print("📥 Installing Python dependencies...")
        try:
            subprocess.run(
                ["poetry", "install", "--with", "dev"], 
                cwd=self.forge_path, 
                check=True,
                capture_output=True
            )
            print("✅ Python dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            raise

    async def configure_system(self):
        """Configure Connor system settings."""
        print("\n⚙️  Configuring system...")
        
        # Load configuration
        config_file = self.project_root / "connor_config.json"
        if config_file.exists():
            with open(config_file) as f:
                self.config = json.load(f)
            print("✅ Loaded existing configuration")
        else:
            # Create default configuration
            self.config = {
                "system": {
                    "max_agents": 50,
                    "max_families": 10,
                    "processing_timeout": 300,
                    "health_check_interval": 30
                },
                "agents": {
                    "sra": {"instances": 3, "priority": 1},
                    "mbr": {"instances": 2, "priority": 2},
                    "gap": {"instances": 2, "priority": 3},
                    "la": {"instances": 4, "priority": 4},
                    "uba": {"instances": 2, "priority": 5},
                    "aa": {"instances": 3, "priority": 6}
                },
                "learning": {
                    "pattern_retention_days": 30,
                    "performance_history_days": 7,
                    "auto_optimize": True
                },
                "monitoring": {
                    "enabled": True,
                    "log_level": "INFO",
                    "alert_thresholds": {
                        "health_score": 70,
                        "processing_time": 10.0,
                        "memory_usage": 85
                    }
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("✅ Created default configuration")
        
        # Apply configuration
        os.environ.update({
            "CONNOR_MAX_AGENTS": str(self.config["system"]["max_agents"]),
            "CONNOR_MAX_FAMILIES": str(self.config["system"]["max_families"]),
            "CONNOR_PROCESSING_TIMEOUT": str(self.config["system"]["processing_timeout"])
        })
        print("✅ Applied system configuration")

    async def run_tests(self):
        """Run deployment verification tests."""
        print("\n🧪 Running deployment tests...")
        
        # Run basic import test
        try:
            test_script = '''
import sys
sys.path.append("/home/runner/work/Connor/Connor/autogpts/forge")
try:
    from forge.connor import ConnorSystem
    print("✅ Connor imports successful")
except ImportError as e:
    print(f"❌ Connor import failed: {e}")
    exit(1)
'''
            result = subprocess.run([sys.executable, "-c", test_script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Import tests passed")
            else:
                print(f"❌ Import tests failed: {result.stderr}")
                raise Exception("Import tests failed")
        except Exception as e:
            print(f"❌ Failed to run import tests: {e}")
            raise
        
        # Run standalone test if available
        standalone_test = self.project_root / "standalone_test.py"
        if standalone_test.exists():
            try:
                result = subprocess.run([sys.executable, str(standalone_test)], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print("✅ Standalone tests passed")
                else:
                    print(f"⚠️  Standalone tests had issues: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("⚠️  Standalone tests timed out")
            except Exception as e:
                print(f"⚠️  Standalone tests failed: {e}")

    async def post_deployment_setup(self):
        """Setup post-deployment services and monitoring."""
        print("\n🔧 Post-deployment setup...")
        
        # Create systemd service file if on Linux
        if sys.platform.startswith('linux'):
            await self.create_systemd_service()
        
        # Setup log rotation
        await self.setup_log_rotation()
        
        # Create monitoring cron job
        await self.setup_monitoring_cron()
        
        # Generate deployment report
        await self.generate_deployment_report()

    async def create_systemd_service(self):
        """Create systemd service for Connor."""
        try:
            service_content = f"""[Unit]
Description=Connor Multi-Agent System
After=network.target

[Service]
Type=simple
User=runner
WorkingDirectory={self.forge_path}
ExecStart={sys.executable} -m forge.app
Restart=always
RestartSec=10
Environment=PYTHONPATH={self.forge_path}

[Install]
WantedBy=multi-user.target
"""
            service_file = Path("/tmp/connor.service")
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            print("✅ Systemd service file created at /tmp/connor.service")
            print("   To install: sudo cp /tmp/connor.service /etc/systemd/system/")
            print("   To enable: sudo systemctl enable connor")
            print("   To start: sudo systemctl start connor")
            
        except Exception as e:
            print(f"⚠️  Could not create systemd service: {e}")

    async def setup_log_rotation(self):
        """Setup log rotation configuration."""
        try:
            logrotate_content = f"""{self.project_root}/logs/*.log {{
    daily
    missingok
    rotate 30
    compress
    delaycompress
    copytruncate
    notifempty
}}
"""
            logrotate_file = Path("/tmp/connor-logrotate")
            with open(logrotate_file, 'w') as f:
                f.write(logrotate_content)
            
            print("✅ Log rotation config created at /tmp/connor-logrotate")
            print("   To install: sudo cp /tmp/connor-logrotate /etc/logrotate.d/connor")
            
        except Exception as e:
            print(f"⚠️  Could not create log rotation config: {e}")

    async def setup_monitoring_cron(self):
        """Setup cron job for monitoring."""
        try:
            cron_content = f"*/5 * * * * {sys.executable} {self.project_root}/scripts/monitor.py --one-shot >> {self.project_root}/logs/cron_health.log 2>&1\n"
            
            cron_file = Path("/tmp/connor-cron")
            with open(cron_file, 'w') as f:
                f.write(cron_content)
            
            print("✅ Cron job created at /tmp/connor-cron")
            print("   To install: crontab /tmp/connor-cron")
            
        except Exception as e:
            print(f"⚠️  Could not create cron job: {e}")

    async def generate_deployment_report(self):
        """Generate deployment summary report."""
        report = {
            "deployment_time": str(asyncio.get_event_loop().time()),
            "target_environment": self.target_env,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "project_root": str(self.project_root),
            "configuration": self.config,
            "status": "completed"
        }
        
        report_file = self.project_root / "reports" / "deployment_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Deployment report saved to {report_file}")

    async def rollback(self):
        """Rollback deployment in case of failure."""
        print("\n🔄 Rolling back deployment...")
        
        # Stop any running services
        try:
            subprocess.run(["pkill", "-f", "connor"], check=False)
            print("✅ Stopped running Connor processes")
        except Exception:
            pass
        
        # Remove temporary files
        temp_files = [
            "/tmp/connor.service",
            "/tmp/connor-logrotate", 
            "/tmp/connor-cron"
        ]
        
        for temp_file in temp_files:
            try:
                Path(temp_file).unlink(missing_ok=True)
                print(f"✅ Removed {temp_file}")
            except Exception:
                pass
        
        print("✅ Rollback completed")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Connor System Deployment")
    parser.add_argument("--env", default="local", choices=["local", "dev", "staging", "production"],
                       help="Target environment (default: local)")
    parser.add_argument("--rollback", action="store_true", help="Rollback deployment")
    
    args = parser.parse_args()
    
    deployer = ConnorDeployment(target_env=args.env)
    
    if args.rollback:
        await deployer.rollback()
    else:
        await deployer.deploy()

if __name__ == "__main__":
    asyncio.run(main())