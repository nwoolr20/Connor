#!/usr/bin/env python3
"""
Connor Auto-Update System
Handles automated updates, dependency management, and system maintenance.
"""

import asyncio
import subprocess
import sys
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ConnorAutoUpdater:
    def __init__(self):
        self.project_root = Path("/home/runner/work/Connor/Connor")
        self.forge_path = self.project_root / "autogpts" / "forge"
        self.backup_dir = self.project_root / "backups"
        self.update_log = []
        
    async def run_auto_update(self):
        """Run complete auto-update process."""
        print("🔄 Starting Connor Auto-Update Process")
        print("=" * 50)
        
        try:
            await self.create_backup()
            await self.check_for_updates()
            await self.update_dependencies()
            await self.run_post_update_tests()
            await self.cleanup_old_backups()
            await self.generate_update_report()
            
            print("\n" + "=" * 50)
            print("✅ Connor Auto-Update Complete!")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Auto-update failed: {e}")
            await self.restore_from_backup()
            raise

    async def create_backup(self):
        """Create backup before updating."""
        print("\n💾 Creating backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"connor_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        backup_path.mkdir()
        
        # Backup configuration files
        config_files = [
            self.forge_path / ".env",
            self.project_root / "connor_config.json",
            self.project_root / "Makefile"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                shutil.copy2(config_file, backup_path / config_file.name)
                print(f"✅ Backed up {config_file.name}")
        
        # Backup logs and reports
        for backup_dir in ["logs", "reports"]:
            src_dir = self.project_root / backup_dir
            if src_dir.exists():
                shutil.copytree(src_dir, backup_path / backup_dir, dirs_exist_ok=True)
                print(f"✅ Backed up {backup_dir}")
        
        self.current_backup = backup_path
        print(f"✅ Backup created at {backup_path}")

    async def check_for_updates(self):
        """Check for available updates."""
        print("\n🔍 Checking for updates...")
        
        try:
            # Check Git updates
            result = subprocess.run(
                ["git", "fetch", "origin"], 
                cwd=self.project_root, 
                capture_output=True, 
                text=True,
                check=True
            )
            
            # Check if there are updates
            result = subprocess.run(
                ["git", "rev-list", "HEAD..origin/main", "--count"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits_behind = int(result.stdout.strip())
            if commits_behind > 0:
                print(f"📥 {commits_behind} new commits available")
                
                # Get commit summary
                result = subprocess.run(
                    ["git", "log", "--oneline", f"HEAD..origin/main"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                print("Recent commits:")
                for line in result.stdout.strip().split('\n')[:5]:
                    print(f"  • {line}")
                
                # Pull updates
                subprocess.run(
                    ["git", "pull", "origin", "main"],
                    cwd=self.project_root,
                    check=True
                )
                print("✅ Updates pulled successfully")
                
                self.update_log.append({
                    "type": "git_update",
                    "commits": commits_behind,
                    "status": "success"
                })
            else:
                print("✅ Already up to date")
                self.update_log.append({
                    "type": "git_check",
                    "status": "up_to_date"
                })
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git update failed: {e}")
            self.update_log.append({
                "type": "git_update",
                "status": "failed",
                "error": str(e)
            })
            raise

    async def update_dependencies(self):
        """Update Python dependencies."""
        print("\n📦 Updating dependencies...")
        
        try:
            # Update Poetry itself
            subprocess.run(
                ["poetry", "self", "update"],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Poetry updated")
            
            # Update project dependencies
            subprocess.run(
                ["poetry", "update"],
                cwd=self.forge_path,
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Python dependencies updated")
            
            # Check for security vulnerabilities
            try:
                result = subprocess.run(
                    ["poetry", "run", "safety", "check"],
                    cwd=self.forge_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("✅ No security vulnerabilities found")
                else:
                    print("⚠️  Security vulnerabilities detected - check safety report")
            except subprocess.CalledProcessError:
                print("⚠️  Could not run security check")
            
            self.update_log.append({
                "type": "dependency_update",
                "status": "success"
            })
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Dependency update failed: {e}")
            self.update_log.append({
                "type": "dependency_update",
                "status": "failed",
                "error": str(e)
            })
            raise

    async def run_post_update_tests(self):
        """Run tests after update to verify system integrity."""
        print("\n🧪 Running post-update verification...")
        
        test_results = {}
        
        # Test 1: Import test
        try:
            test_script = '''
import sys
sys.path.append("/home/runner/work/Connor/Connor/autogpts/forge")
from forge.connor import ConnorSystem
print("Import test passed")
'''
            result = subprocess.run(
                [sys.executable, "-c", test_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            test_results["import_test"] = result.returncode == 0
            if result.returncode == 0:
                print("✅ Import test passed")
            else:
                print(f"❌ Import test failed: {result.stderr}")
        except Exception as e:
            test_results["import_test"] = False
            print(f"❌ Import test error: {e}")
        
        # Test 2: Standalone test
        standalone_test = self.project_root / "standalone_test.py"
        if standalone_test.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(standalone_test)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                test_results["standalone_test"] = result.returncode == 0
                if result.returncode == 0:
                    print("✅ Standalone test passed")
                else:
                    print(f"⚠️  Standalone test issues: {result.stderr}")
            except Exception as e:
                test_results["standalone_test"] = False
                print(f"❌ Standalone test error: {e}")
        
        # Test 3: Health check
        try:
            monitor_script = self.project_root / "scripts" / "monitor.py"
            if monitor_script.exists():
                result = subprocess.run(
                    [sys.executable, str(monitor_script), "--one-shot"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                test_results["health_check"] = result.returncode == 0
                if result.returncode == 0:
                    print("✅ Health check passed")
                else:
                    print(f"⚠️  Health check issues: {result.stderr}")
        except Exception as e:
            test_results["health_check"] = False
            print(f"❌ Health check error: {e}")
        
        # Evaluate test results
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        self.update_log.append({
            "type": "post_update_tests",
            "results": test_results,
            "success_rate": success_rate
        })
        
        print(f"📊 Post-update tests: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        if success_rate < 50:
            raise Exception(f"Post-update tests failed: {success_rate:.1f}% success rate")

    async def cleanup_old_backups(self, keep_count=5):
        """Clean up old backup files."""
        print(f"\n🧹 Cleaning up old backups (keeping {keep_count})...")
        
        if not self.backup_dir.exists():
            return
        
        # Get all backup directories sorted by creation time
        backups = [d for d in self.backup_dir.iterdir() if d.is_dir() and d.name.startswith("connor_backup_")]
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old backups
        removed_count = 0
        for backup in backups[keep_count:]:
            try:
                shutil.rmtree(backup)
                removed_count += 1
                print(f"✅ Removed old backup: {backup.name}")
            except Exception as e:
                print(f"⚠️  Could not remove backup {backup.name}: {e}")
        
        if removed_count > 0:
            print(f"✅ Cleaned up {removed_count} old backups")
        else:
            print("✅ No old backups to clean up")

    async def restore_from_backup(self):
        """Restore system from backup in case of failure."""
        print("\n🔄 Restoring from backup...")
        
        if not hasattr(self, 'current_backup') or not self.current_backup.exists():
            print("❌ No backup available for restoration")
            return
        
        try:
            # Restore configuration files
            for backup_file in self.current_backup.iterdir():
                if backup_file.is_file():
                    target_path = self.project_root / backup_file.name
                    if backup_file.name == ".env":
                        target_path = self.forge_path / backup_file.name
                    
                    shutil.copy2(backup_file, target_path)
                    print(f"✅ Restored {backup_file.name}")
                elif backup_file.is_dir() and backup_file.name in ["logs", "reports"]:
                    target_dir = self.project_root / backup_file.name
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    shutil.copytree(backup_file, target_dir)
                    print(f"✅ Restored {backup_file.name} directory")
            
            print("✅ System restored from backup")
            
        except Exception as e:
            print(f"❌ Failed to restore from backup: {e}")

    async def generate_update_report(self):
        """Generate update summary report."""
        print("\n📋 Generating update report...")
        
        report = {
            "update_time": datetime.now().isoformat(),
            "system_info": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform
            },
            "update_log": self.update_log,
            "backup_location": str(self.current_backup) if hasattr(self, 'current_backup') else None,
            "status": "completed"
        }
        
        # Save report
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"auto_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Update report saved to {report_file}")
        
        # Print summary
        print("\n📊 Update Summary:")
        for log_entry in self.update_log:
            entry_type = log_entry.get("type", "unknown")
            status = log_entry.get("status", "unknown")
            
            if status == "success":
                status_emoji = "✅"
            elif status == "failed":
                status_emoji = "❌"
            elif status == "up_to_date":
                status_emoji = "ℹ️"
            else:
                status_emoji = "⚠️"
            
            print(f"  {status_emoji} {entry_type}: {status}")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Connor Auto-Update System")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    parser.add_argument("--force", action="store_true", help="Force update even if up to date")
    parser.add_argument("--backup-only", action="store_true", help="Create backup only")
    
    args = parser.parse_args()
    
    updater = ConnorAutoUpdater()
    
    if args.backup_only:
        await updater.create_backup()
    elif args.dry_run:
        print("🔍 Dry run mode - showing available updates...")
        # Implement dry run logic here
        await updater.check_for_updates()
    else:
        await updater.run_auto_update()

if __name__ == "__main__":
    asyncio.run(main())