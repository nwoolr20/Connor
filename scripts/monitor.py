#!/usr/bin/env python3
"""
Connor System Monitor
Provides automated monitoring and health checking for the Connor multi-agent system.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add the forge directory to the Python path
sys.path.append('/home/runner/work/Connor/Connor/autogpts/forge')

try:
    from forge.connor import ConnorSystem
except ImportError:
    print("⚠️  Connor system not available - running in monitoring-only mode")
    ConnorSystem = None

class ConnorMonitor:
    def __init__(self, log_dir="logs", check_interval=30):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.check_interval = check_interval
        self.connor_system = None
        self.metrics = {
            "start_time": datetime.now(),
            "checks_performed": 0,
            "health_checks": [],
            "performance_metrics": [],
            "alerts": []
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / 'connor_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def initialize_connor(self):
        """Initialize Connor system for monitoring."""
        if ConnorSystem is None:
            self.logger.warning("Connor system not available")
            return False
            
        try:
            self.connor_system = ConnorSystem()
            self.logger.info("✅ Connor system initialized for monitoring")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Connor system: {e}")
            return False

    async def check_system_health(self):
        """Perform comprehensive system health check."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Basic system checks
        health_report["checks"]["python_version"] = self.check_python_version()
        health_report["checks"]["dependencies"] = await self.check_dependencies()
        health_report["checks"]["disk_space"] = self.check_disk_space()
        health_report["checks"]["memory_usage"] = self.check_memory_usage()
        
        # Connor-specific checks
        if self.connor_system:
            health_report["checks"]["connor_system"] = await self.check_connor_health()
            health_report["checks"]["agent_status"] = await self.check_agent_status()
            health_report["checks"]["performance"] = await self.check_performance()
        
        # Calculate overall health score
        passed_checks = sum(1 for check in health_report["checks"].values() if check.get("status") == "healthy")
        total_checks = len(health_report["checks"])
        health_report["health_score"] = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        self.metrics["health_checks"].append(health_report)
        self.metrics["checks_performed"] += 1
        
        # Log health status
        if health_report["health_score"] >= 80:
            self.logger.info(f"✅ System health: {health_report['health_score']:.1f}% ({passed_checks}/{total_checks} checks passed)")
        elif health_report["health_score"] >= 60:
            self.logger.warning(f"⚠️ System health: {health_report['health_score']:.1f}% ({passed_checks}/{total_checks} checks passed)")
        else:
            self.logger.error(f"❌ System health: {health_report['health_score']:.1f}% ({passed_checks}/{total_checks} checks passed)")
            await self.create_alert("Low system health", health_report)
        
        return health_report

    def check_python_version(self):
        """Check Python version compatibility."""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            return {"status": "healthy", "version": f"{version.major}.{version.minor}.{version.micro}"}
        else:
            return {"status": "unhealthy", "version": f"{version.major}.{version.minor}.{version.micro}", "issue": "Python 3.8+ required"}

    async def check_dependencies(self):
        """Check critical dependencies."""
        dependencies = {
            "asyncio": True,
            "json": True,
            "pathlib": True,
            "logging": True
        }
        
        issues = []
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                issues.append(dep)
                dependencies[dep] = False
        
        if issues:
            return {"status": "unhealthy", "missing": issues, "available": dependencies}
        else:
            return {"status": "healthy", "all_dependencies": "available"}

    def check_disk_space(self):
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_gb = free // (1024**3)
            percent_free = (free / total) * 100
            
            if percent_free < 10:
                return {"status": "unhealthy", "free_gb": free_gb, "percent_free": percent_free, "issue": "Low disk space"}
            elif percent_free < 20:
                return {"status": "warning", "free_gb": free_gb, "percent_free": percent_free, "issue": "Disk space getting low"}
            else:
                return {"status": "healthy", "free_gb": free_gb, "percent_free": percent_free}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def check_memory_usage(self):
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            
            if percent_used > 90:
                return {"status": "unhealthy", "percent_used": percent_used, "issue": "High memory usage"}
            elif percent_used > 80:
                return {"status": "warning", "percent_used": percent_used, "issue": "Memory usage elevated"}
            else:
                return {"status": "healthy", "percent_used": percent_used}
        except ImportError:
            return {"status": "unknown", "note": "psutil not available for memory monitoring"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_connor_health(self):
        """Check Connor system health."""
        try:
            status = self.connor_system.get_system_status()
            
            if status["total_agents"] > 0:
                return {"status": "healthy", "agents": status["total_agents"], "families": status["families"]}
            else:
                return {"status": "unhealthy", "issue": "No agents available"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_agent_status(self):
        """Check individual agent status."""
        try:
            status = self.connor_system.get_system_status()
            agent_distribution = status.get("agent_distribution", {})
            
            required_agents = ["SRA", "MBR", "GAP", "LA", "UBA", "AA"]
            missing_agents = [agent for agent in required_agents if agent_distribution.get(agent, 0) == 0]
            
            if missing_agents:
                return {"status": "unhealthy", "missing_agents": missing_agents, "distribution": agent_distribution}
            else:
                return {"status": "healthy", "all_agents_present": True, "distribution": agent_distribution}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_performance(self):
        """Check system performance metrics."""
        try:
            # Test simple processing speed
            start_time = time.time()
            test_response = await self.connor_system.process_input("Test input for performance monitoring", priority=3)
            processing_time = time.time() - start_time
            
            performance_data = {
                "processing_time": processing_time,
                "success": test_response.get("success", False),
                "confidence": test_response.get("system_confidence", 0.0)
            }
            
            if processing_time > 10.0:
                performance_data["status"] = "unhealthy"
                performance_data["issue"] = "Slow processing time"
            elif processing_time > 5.0:
                performance_data["status"] = "warning"
                performance_data["issue"] = "Processing time elevated"
            else:
                performance_data["status"] = "healthy"
            
            self.metrics["performance_metrics"].append(performance_data)
            return performance_data
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def create_alert(self, alert_type, details):
        """Create alert for significant issues."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "details": details,
            "severity": "high" if details.get("health_score", 100) < 50 else "medium"
        }
        
        self.metrics["alerts"].append(alert)
        self.logger.error(f"🚨 ALERT: {alert_type} - {alert['severity']} severity")
        
        # Write alert to file
        alert_file = self.log_dir / f"alert_{int(time.time())}.json"
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2)

    async def save_metrics(self):
        """Save monitoring metrics to file."""
        metrics_file = self.log_dir / "connor_metrics.json"
        
        # Convert datetime objects to strings for JSON serialization
        metrics_copy = self.metrics.copy()
        metrics_copy["start_time"] = metrics_copy["start_time"].isoformat()
        metrics_copy["uptime_hours"] = (datetime.now() - self.metrics["start_time"]).total_seconds() / 3600
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics_copy, f, indent=2, default=str)

    async def cleanup_old_logs(self, days_to_keep=7):
        """Clean up old log files."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                self.logger.info(f"Cleaned up old log file: {log_file.name}")

    async def run_monitoring_cycle(self):
        """Run one complete monitoring cycle."""
        self.logger.info("🔍 Starting monitoring cycle")
        
        try:
            health_report = await self.check_system_health()
            await self.save_metrics()
            
            # Cleanup old logs daily
            if self.metrics["checks_performed"] % (24 * 3600 // self.check_interval) == 0:
                await self.cleanup_old_logs()
            
            self.logger.info(f"✅ Monitoring cycle complete - Health: {health_report['health_score']:.1f}%")
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring cycle failed: {e}")
            await self.create_alert("Monitoring cycle failure", {"error": str(e)})

    async def run(self):
        """Run continuous monitoring."""
        self.logger.info("🚀 Starting Connor System Monitor")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        
        # Initialize Connor system
        await self.initialize_connor()
        
        try:
            while True:
                await self.run_monitoring_cycle()
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Monitor crashed: {e}")
            await self.create_alert("Monitor crash", {"error": str(e)})
        finally:
            await self.save_metrics()
            self.logger.info("💾 Final metrics saved")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Connor System Monitor")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds (default: 30)")
    parser.add_argument("--log-dir", default="logs", help="Log directory (default: logs)")
    parser.add_argument("--one-shot", action="store_true", help="Run single health check and exit")
    
    args = parser.parse_args()
    
    monitor = ConnorMonitor(log_dir=args.log_dir, check_interval=args.interval)
    
    if args.one_shot:
        print("🔍 Running single health check...")
        await monitor.initialize_connor()
        health_report = await monitor.check_system_health()
        print(f"Health Score: {health_report['health_score']:.1f}%")
        print(json.dumps(health_report, indent=2, default=str))
    else:
        await monitor.run()

if __name__ == "__main__":
    asyncio.run(main())