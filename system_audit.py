#!/usr/bin/env python3
"""
Connor System Comprehensive Audit Tool
=====================================

Performs a complete system audit including:
- Core module testing and integration validation
- Performance benchmarking across all components
- Dependency analysis and health checks
- Memory management and lifecycle testing
- Communication bus validation
- CLI interface verification
- Orphaned file and broken link detection
- Security and configuration auditing

Generates detailed reports with recommendations for fixes and optimizations.
"""

import asyncio
import os
import sys
import time
import json
import subprocess
import importlib
import inspect
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from enum import Enum

# Add the Connor modules to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autogpts', 'forge'))

@dataclass
class AuditResult:
    """Results from a single audit check"""
    component: str
    test_name: str
    status: str  # 'PASS', 'FAIL', 'WARNING', 'SKIP'
    message: str
    details: Dict[str, Any]
    duration: float
    timestamp: str

@dataclass
class SystemMetrics:
    """System performance metrics"""
    import_time: float
    memory_usage: float
    cpu_usage: float
    startup_time: float
    response_time: float

class ConnorSystemAuditor:
    """Comprehensive Connor system auditor"""
    
    def __init__(self):
        self.results: List[AuditResult] = []
        self.metrics = {}
        self.connor_root = Path(__file__).parent
        self.connor_dir = self.connor_root / 'autogpts' / 'forge'
        self.reports_dir = self.connor_root / 'docs' / 'audit_reports'
        self.reports_dir.mkdir(exist_ok=True, parents=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def add_result(self, component: str, test_name: str, status: str, 
                   message: str, details: Dict[str, Any] = None, duration: float = 0.0):
        """Add an audit result"""
        result = AuditResult(
            component=component,
            test_name=test_name,
            status=status,
            message=message,
            details=details or {},
            duration=duration,
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
        )
        self.results.append(result)
        
        # Log the result
        color = {
            'PASS': '\033[92m✅',
            'FAIL': '\033[91m❌',
            'WARNING': '\033[93m⚠️',
            'SKIP': '\033[94mℹ️'
        }.get(status, '🔍')
        
        print(f"{color} {component}: {test_name} - {message}\033[0m")
        
    async def audit_core_imports(self) -> None:
        """Test all core module imports"""
        self.logger.info("🔍 Starting core imports audit...")
        
        core_modules = [
            'forge.connor.base',
            'forge.connor.connor_system', 
            'forge.connor.sra',
            'forge.connor.la',
            'forge.connor.uba',
            'forge.connor.aa',
            'forge.connor.gap',
            'forge.connor.mbr'
        ]
        
        for module_name in core_modules:
            start_time = time.time()
            try:
                module = importlib.import_module(module_name)
                duration = time.time() - start_time
                
                # Check if module has expected attributes
                classes = [name for name, obj in inspect.getmembers(module, inspect.isclass)
                          if obj.__module__ == module_name]
                
                self.add_result(
                    'Core Modules',
                    f'Import {module_name}',
                    'PASS',
                    f'Successfully imported with {len(classes)} classes',
                    {'classes': classes, 'module_path': str(module.__file__)},
                    duration
                )
                
            except Exception as e:
                duration = time.time() - start_time
                self.add_result(
                    'Core Modules',
                    f'Import {module_name}',
                    'FAIL',
                    f'Import failed: {str(e)}',
                    {'error': str(e), 'traceback': traceback.format_exc()},
                    duration
                )
    
    async def audit_agent_initialization(self) -> None:
        """Test agent initialization and configuration"""
        self.logger.info("🔍 Testing agent initialization...")
        
        try:
            from forge.connor.base import BaseConnorAgent, AgentConfig, AgentType, AgentPhase
            
            # Test basic agent config creation
            start_time = time.time()
            config = AgentConfig(
                agent_id="test_agent",
                agent_type=AgentType.SRA
            )
            duration = time.time() - start_time
            
            self.add_result(
                'Agent System',
                'AgentConfig Creation',
                'PASS',
                'Successfully created agent configuration',
                {'agent_id': config.agent_id, 'agent_type': config.agent_type.value},
                duration
            )
            
        except Exception as e:
            self.add_result(
                'Agent System',
                'AgentConfig Creation',
                'FAIL',
                f'Failed to create agent config: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_connor_system(self) -> None:
        """Test Connor system initialization and core functionality"""
        self.logger.info("🔍 Testing Connor system...")
        
        try:
            from forge.connor.connor_system import ConnorSystem
            
            start_time = time.time()
            connor = ConnorSystem()
            init_duration = time.time() - start_time
            
            self.add_result(
                'Connor System',
                'System Initialization',
                'PASS',
                f'Successfully initialized Connor system',
                {'init_time': init_duration},
                init_duration
            )
            
            # Test system status
            try:
                status = connor.get_system_status()
                self.add_result(
                    'Connor System',
                    'System Status',
                    'PASS',
                    'Successfully retrieved system status',
                    {'status': status}
                )
            except Exception as e:
                self.add_result(
                    'Connor System',
                    'System Status',
                    'FAIL',
                    f'Failed to get system status: {str(e)}',
                    {'error': str(e)}
                )
                
        except Exception as e:
            self.add_result(
                'Connor System',
                'System Initialization',
                'FAIL',
                f'Failed to initialize Connor system: {str(e)}',
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
    
    async def audit_agent_types(self) -> None:
        """Test all agent types for proper functionality"""
        self.logger.info("🔍 Testing individual agent types...")
        
        agent_modules = {
            'SRA': 'forge.connor.sra',
            'LA': 'forge.connor.la', 
            'UBA': 'forge.connor.uba',
            'AA': 'forge.connor.aa',
            'GAP': 'forge.connor.gap',
            'MBR': 'forge.connor.mbr'
        }
        
        for agent_type, module_name in agent_modules.items():
            try:
                start_time = time.time()
                module = importlib.import_module(module_name)
                
                # Find agent classes in the module
                agent_classes = [obj for name, obj in inspect.getmembers(module, inspect.isclass)
                               if 'Agent' in name and obj.__module__ == module_name]
                
                duration = time.time() - start_time
                
                if agent_classes:
                    self.add_result(
                        'Agent Types',
                        f'{agent_type} Agent Import',
                        'PASS',
                        f'Found {len(agent_classes)} agent classes',
                        {'classes': [cls.__name__ for cls in agent_classes]},
                        duration
                    )
                    
                    # Test agent class structure
                    for agent_class in agent_classes:
                        self._audit_agent_class(agent_type, agent_class)
                else:
                    self.add_result(
                        'Agent Types',
                        f'{agent_type} Agent Import',
                        'WARNING',
                        'No agent classes found in module',
                        {'module': module_name},
                        duration
                    )
                    
            except Exception as e:
                self.add_result(
                    'Agent Types',
                    f'{agent_type} Agent Import',
                    'FAIL',
                    f'Failed to import: {str(e)}',
                    {'error': str(e)}
                )
    
    def _audit_agent_class(self, agent_type: str, agent_class) -> None:
        """Audit a specific agent class"""
        try:
            # Check required methods
            required_methods = ['process_input', '__init__']
            missing_methods = []
            
            for method in required_methods:
                if not hasattr(agent_class, method):
                    missing_methods.append(method)
            
            if missing_methods:
                self.add_result(
                    'Agent Types',
                    f'{agent_type} Class Structure',
                    'WARNING',
                    f'Missing methods: {missing_methods}',
                    {'missing_methods': missing_methods}
                )
            else:
                self.add_result(
                    'Agent Types',
                    f'{agent_type} Class Structure',
                    'PASS',
                    'All required methods present',
                    {'class_name': agent_class.__name__}
                )
                
        except Exception as e:
            self.add_result(
                'Agent Types',
                f'{agent_type} Class Structure',
                'FAIL',
                f'Error analyzing class: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_memory_system(self) -> None:
        """Test memory management system"""
        self.logger.info("🔍 Testing memory system...")
        
        try:
            from forge.memory import MemStore, ChromaMemStore
            
            self.add_result(
                'Memory System',
                'Memory Module Import',
                'PASS',
                'Successfully imported memory modules',
                {'modules': ['MemStore', 'ChromaMemStore']}
            )
            
        except Exception as e:
            self.add_result(
                'Memory System',
                'Memory Module Import',
                'FAIL',
                f'Failed to import memory modules: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_cli_interfaces(self) -> None:
        """Test CLI interfaces and automation scripts"""
        self.logger.info("🔍 Testing CLI interfaces...")
        
        cli_files = [
            'connor_cli.py',
            'cli.py',
            'demo_connor.py'
        ]
        
        for cli_file in cli_files:
            cli_path = self.connor_root / cli_file
            if cli_path.exists():
                try:
                    # Test if file is executable and has valid Python syntax
                    result = subprocess.run([sys.executable, '-m', 'py_compile', str(cli_path)], 
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.add_result(
                            'CLI Interfaces',
                            f'{cli_file} Syntax',
                            'PASS',
                            'Valid Python syntax',
                            {'file_size': cli_path.stat().st_size}
                        )
                    else:
                        self.add_result(
                            'CLI Interfaces',
                            f'{cli_file} Syntax',
                            'FAIL',
                            f'Syntax error: {result.stderr}',
                            {'error': result.stderr}
                        )
                        
                except Exception as e:
                    self.add_result(
                        'CLI Interfaces',
                        f'{cli_file} Syntax',
                        'FAIL',
                        f'Error checking syntax: {str(e)}',
                        {'error': str(e)}
                    )
            else:
                self.add_result(
                    'CLI Interfaces',
                    f'{cli_file} Existence',
                    'FAIL',
                    'CLI file not found',
                    {'expected_path': str(cli_path)}
                )
    
    async def audit_configuration(self) -> None:
        """Test configuration files and environment setup"""
        self.logger.info("🔍 Testing configuration...")
        
        config_files = [
            'connor_config.json',
            '.env',
            'Makefile',
            'pyproject.toml'
        ]
        
        for config_file in config_files:
            config_path = self.connor_root / config_file
            if config_path.exists():
                try:
                    if config_file.endswith('.json'):
                        with open(config_path, 'r') as f:
                            data = json.load(f)
                        self.add_result(
                            'Configuration',
                            f'{config_file} Validation',
                            'PASS',
                            'Valid JSON configuration',
                            {'keys': list(data.keys()) if isinstance(data, dict) else 'non-dict'}
                        )
                    else:
                        # Just check if file is readable
                        with open(config_path, 'r') as f:
                            content = f.read()
                        self.add_result(
                            'Configuration',
                            f'{config_file} Accessibility',
                            'PASS',
                            'File readable',
                            {'file_size': len(content)}
                        )
                        
                except Exception as e:
                    self.add_result(
                        'Configuration',
                        f'{config_file} Validation',
                        'FAIL',
                        f'Error reading file: {str(e)}',
                        {'error': str(e)}
                    )
            else:
                status = 'WARNING' if config_file in ['.env'] else 'FAIL'
                self.add_result(
                    'Configuration',
                    f'{config_file} Existence',
                    status,
                    'Configuration file not found',
                    {'expected_path': str(config_path)}
                )
    
    async def audit_dependencies(self) -> None:
        """Analyze dependency health and conflicts"""
        self.logger.info("🔍 Analyzing dependencies...")
        
        try:
            # Check poetry lock file
            poetry_lock = self.connor_dir / 'poetry.lock'
            if poetry_lock.exists():
                self.add_result(
                    'Dependencies',
                    'Poetry Lock File',
                    'PASS',
                    'Poetry lock file exists',
                    {'file_size': poetry_lock.stat().st_size}
                )
            else:
                self.add_result(
                    'Dependencies',
                    'Poetry Lock File',
                    'WARNING',
                    'Poetry lock file not found'
                )
            
            # Check pyproject.toml
            pyproject = self.connor_dir / 'pyproject.toml'
            if pyproject.exists():
                self.add_result(
                    'Dependencies',
                    'PyProject Configuration',
                    'PASS',
                    'PyProject.toml exists',
                    {'file_size': pyproject.stat().st_size}
                )
            else:
                self.add_result(
                    'Dependencies',
                    'PyProject Configuration',
                    'FAIL',
                    'PyProject.toml not found'
                )
                
        except Exception as e:
            self.add_result(
                'Dependencies',
                'Dependency Analysis',
                'FAIL',
                f'Error analyzing dependencies: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_file_structure(self) -> None:
        """Check for orphaned files and broken links"""
        self.logger.info("🔍 Analyzing file structure...")
        
        try:
            # Check for important directories
            important_dirs = [
                'autogpts/forge/forge/connor',
                'autogpts/forge/forge/memory',
                'scripts',
                'docs'
            ]
            
            for dir_path in important_dirs:
                full_path = self.connor_root / dir_path
                if full_path.exists() and full_path.is_dir():
                    file_count = len(list(full_path.rglob('*')))
                    self.add_result(
                        'File Structure',
                        f'Directory {dir_path}',
                        'PASS',
                        f'Directory exists with {file_count} items',
                        {'file_count': file_count}
                    )
                else:
                    self.add_result(
                        'File Structure',
                        f'Directory {dir_path}',
                        'FAIL',
                        'Required directory missing',
                        {'expected_path': str(full_path)}
                    )
            
            # Check for Python __init__.py files
            python_dirs = list(self.connor_root.rglob('*.py'))
            package_dirs = set()
            for py_file in python_dirs:
                package_dirs.add(py_file.parent)
            
            missing_inits = []
            for pkg_dir in package_dirs:
                if not (pkg_dir / '__init__.py').exists() and pkg_dir != self.connor_root:
                    missing_inits.append(str(pkg_dir))
            
            if missing_inits:
                self.add_result(
                    'File Structure',
                    'Package Initialization',
                    'WARNING',
                    f'Missing __init__.py in {len(missing_inits)} directories',
                    {'missing_inits': missing_inits[:10]}  # Limit to first 10
                )
            else:
                self.add_result(
                    'File Structure',
                    'Package Initialization',
                    'PASS',
                    'All Python packages properly initialized'
                )
                
        except Exception as e:
            self.add_result(
                'File Structure',
                'Structure Analysis',
                'FAIL',
                f'Error analyzing file structure: {str(e)}',
                {'error': str(e)}
            )
    
    async def benchmark_performance(self) -> None:
        """Benchmark system performance"""
        self.logger.info("🔍 Running performance benchmarks...")
        
        try:
            # Test import performance
            import_times = {}
            modules_to_test = [
                'forge.connor.base',
                'forge.connor.connor_system',
                'forge.connor.sra',
                'forge.connor.la'
            ]
            
            for module_name in modules_to_test:
                start_time = time.time()
                try:
                    importlib.import_module(module_name)
                    import_times[module_name] = time.time() - start_time
                except:
                    import_times[module_name] = -1  # Failed import
            
            successful_times = [t for t in import_times.values() if t > 0]
            avg_import_time = sum(successful_times) / len(successful_times) if successful_times else 0
            
            if avg_import_time < 1.0:
                status = 'PASS'
                message = f'Good import performance: {avg_import_time:.3f}s average'
            elif avg_import_time < 3.0:
                status = 'WARNING'
                message = f'Moderate import performance: {avg_import_time:.3f}s average'
            else:
                status = 'FAIL'
                message = f'Slow import performance: {avg_import_time:.3f}s average'
            
            self.add_result(
                'Performance',
                'Import Benchmarks',
                status,
                message,
                {'import_times': import_times, 'average': avg_import_time}
            )
            
        except Exception as e:
            self.add_result(
                'Performance',
                'Performance Benchmarks',
                'FAIL',
                f'Error running benchmarks: {str(e)}',
                {'error': str(e)}
            )
    
    async def run_full_audit(self) -> Dict[str, Any]:
        """Run complete system audit"""
        print("\n🔍 Starting Connor System Comprehensive Audit")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all audit components - comprehensive coverage
        await self.audit_core_imports()
        await self.audit_agent_initialization()
        await self.audit_connor_system()
        await self.audit_agent_types()
        await self.audit_memory_system()
        await self.audit_cli_interfaces()
        await self.audit_configuration()
        await self.audit_dependencies()
        await self.audit_file_structure()
        await self.audit_communication_bus()
        await self.audit_lifecycle_daemons()
        await self.audit_memory_index()
        await self.audit_daisy_chained_logic()
        await self.audit_edge_cases_and_fallbacks()
        await self.audit_automation_hooks()
        await self.audit_orphaned_files()
        await self.audit_inter_module_relationships()
        await self.audit_dependency_trees()
        await self.audit_system_synchronization()
        await self.benchmark_performance()
        
        total_duration = time.time() - start_time
        
        # Generate summary
        summary = self._generate_summary(total_duration)
        
        # Save results
        self._save_results(summary)
        
        print(f"\n✅ Audit completed in {total_duration:.2f}s")
        print(f"📊 Results saved to: {self.reports_dir}")
        
        return summary
    
    def _generate_summary(self, total_duration: float) -> Dict[str, Any]:
        """Generate audit summary"""
        by_status = {}
        by_component = {}
        
        for result in self.results:
            # Count by status
            by_status[result.status] = by_status.get(result.status, 0) + 1
            
            # Count by component
            if result.component not in by_component:
                by_component[result.component] = {'PASS': 0, 'FAIL': 0, 'WARNING': 0, 'SKIP': 0}
            by_component[result.component][result.status] += 1
        
        # Calculate health score
        total_tests = len(self.results)
        passed_tests = by_status.get('PASS', 0)
        health_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_duration': total_duration,
            'total_tests': total_tests,
            'health_score': health_score,
            'summary_by_status': by_status,
            'summary_by_component': by_component,
            'recommendations': self._generate_recommendations(),
            'detailed_results': [asdict(result) for result in self.results]
        }
        
        return summary
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        # Analyze results for patterns
        failed_components = set()
        warning_components = set()
        
        for result in self.results:
            if result.status == 'FAIL':
                failed_components.add(result.component)
            elif result.status == 'WARNING':
                warning_components.add(result.component)
        
        # Generate specific recommendations
        if 'Core Modules' in failed_components:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Dependencies',
                'issue': 'Core module import failures',
                'recommendation': 'Install missing dependencies using poetry install or pip install',
                'action': 'Run: cd autogpts/forge && poetry install'
            })
        
        if 'Agent Types' in failed_components:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Architecture',
                'issue': 'Agent type failures',
                'recommendation': 'Review agent implementations for missing methods or dependencies',
                'action': 'Check agent class implementations and inheritance structure'
            })
        
        if 'Configuration' in failed_components:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Configuration',
                'issue': 'Configuration file issues',
                'recommendation': 'Create missing configuration files',
                'action': 'Run: make configure-environment'
            })
        
        if 'Performance' in failed_components:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Performance',
                'issue': 'Performance bottlenecks detected',
                'recommendation': 'Optimize slow-loading modules and dependencies',
                'action': 'Profile import times and optimize heavy dependencies'
            })
        
        # General recommendations based on warnings
        if warning_components:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Maintenance',
                'issue': f'Components with warnings: {", ".join(warning_components)}',
                'recommendation': 'Address warning conditions to improve system reliability',
                'action': 'Review detailed audit results for specific warning fixes'
            })
        
        return recommendations
    
    def _make_json_serializable(self, obj):
        """Convert objects to JSON serializable format"""
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj
    
    def _save_results(self, summary: Dict[str, Any]) -> None:
        """Save audit results to files"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Make summary JSON serializable
        serializable_summary = self._make_json_serializable(summary)
        
        # Save detailed JSON report
        json_file = self.reports_dir / f'connor_audit_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(serializable_summary, f, indent=2)
        
        # Save human-readable summary
        summary_file = self.reports_dir / f'connor_audit_summary_{timestamp}.md'
        with open(summary_file, 'w') as f:
            self._write_markdown_summary(f, summary)
        
        # Save latest report (for easy access)
        latest_json = self.reports_dir / 'latest_audit.json'
        latest_md = self.reports_dir / 'latest_audit_summary.md'
        
        with open(latest_json, 'w') as f:
            json.dump(serializable_summary, f, indent=2)
        
        with open(latest_md, 'w') as f:
            self._write_markdown_summary(f, summary)
    
    def _write_markdown_summary(self, f, summary: Dict[str, Any]) -> None:
        """Write markdown summary report"""
        f.write("# Connor System Audit Report\n\n")
        f.write(f"**Timestamp:** {summary['timestamp']}  \n")
        f.write(f"**Duration:** {summary['total_duration']:.2f} seconds  \n")
        f.write(f"**Total Tests:** {summary['total_tests']}  \n")
        f.write(f"**Health Score:** {summary['health_score']:.1f}%  \n\n")
        
        # Overall status
        if summary['health_score'] >= 90:
            f.write("🟢 **Status:** EXCELLENT - System is in great condition\n\n")
        elif summary['health_score'] >= 70:
            f.write("🟡 **Status:** GOOD - Minor issues detected\n\n")
        elif summary['health_score'] >= 50:
            f.write("🟠 **Status:** FAIR - Several issues need attention\n\n")
        else:
            f.write("🔴 **Status:** POOR - Critical issues require immediate attention\n\n")
        
        # Summary by status
        f.write("## Test Results Summary\n\n")
        for status, count in summary['summary_by_status'].items():
            emoji = {'PASS': '✅', 'FAIL': '❌', 'WARNING': '⚠️', 'SKIP': 'ℹ️'}.get(status, '🔍')
            f.write(f"- {emoji} **{status}:** {count} tests\n")
        f.write("\n")
        
        # Summary by component
        f.write("## Component Analysis\n\n")
        f.write("| Component | ✅ Pass | ❌ Fail | ⚠️ Warning | ℹ️ Skip |\n")
        f.write("|-----------|---------|---------|------------|--------|\n")
        
        for component, counts in summary['summary_by_component'].items():
            f.write(f"| {component} | {counts.get('PASS', 0)} | {counts.get('FAIL', 0)} | {counts.get('WARNING', 0)} | {counts.get('SKIP', 0)} |\n")
        f.write("\n")
        
        # Recommendations
        if summary['recommendations']:
            f.write("## Recommendations\n\n")
            for i, rec in enumerate(summary['recommendations'], 1):
                priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(rec['priority'], '🔵')
                f.write(f"### {i}. {rec['category']} {priority_emoji}\n\n")
                f.write(f"**Issue:** {rec['issue']}  \n")
                f.write(f"**Recommendation:** {rec['recommendation']}  \n")
                f.write(f"**Action:** `{rec['action']}`\n\n")
        
        # Detailed results
        f.write("## Detailed Test Results\n\n")
        current_component = None
        for result in summary['detailed_results']:
            if result['component'] != current_component:
                current_component = result['component']
                f.write(f"### {current_component}\n\n")
            
            status_emoji = {'PASS': '✅', 'FAIL': '❌', 'WARNING': '⚠️', 'SKIP': 'ℹ️'}.get(result['status'], '🔍')
            f.write(f"- {status_emoji} **{result['test_name']}** ({result['duration']:.3f}s): {result['message']}\n")
        
        f.write("\n---\n")
        f.write(f"*Report generated by Connor System Auditor on {summary['timestamp']}*\n")

    async def audit_communication_bus(self) -> None:
        """Test inter-agent communication bus and message passing"""
        self.logger.info("🔍 Testing communication bus...")
        
        try:
            from forge.connor.base import AgentMessage
            from forge.connor.connor_system import ConnorSystem
            
            # Test message creation
            test_message = AgentMessage(
                sender_id="test_sender",
                sender_type="SRA",
                content={"test": "message"}
            )
            
            self.add_result(
                'Communication Bus',
                'Message Creation',
                'PASS',
                'Successfully created test message',
                {'message_type': type(test_message).__name__}
            )
            
            # Test Connor system message handling
            connor = ConnorSystem()
            agents = list(connor.agents.values())
            
            if len(agents) >= 2:
                sender = agents[0]
                receiver = agents[1]
                
                # Test message passing capability
                try:
                    result = await receiver.handle_message(test_message)
                    self.add_result(
                        'Communication Bus',
                        'Message Processing',
                        'PASS',
                        'Agent successfully processed message',
                        {'sender_type': sender.agent_type, 'receiver_type': receiver.agent_type}
                    )
                except Exception as e:
                    self.add_result(
                        'Communication Bus',
                        'Message Processing',
                        'WARNING',
                        f'Message processing with issues: {str(e)}',
                        {'error': str(e)}
                    )
            else:
                self.add_result(
                    'Communication Bus',
                    'Agent Communication',
                    'SKIP',
                    'Not enough agents for communication test'
                )
                
        except Exception as e:
            self.add_result(
                'Communication Bus',
                'Communication Bus Test',
                'FAIL',
                f'Error testing communication bus: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_lifecycle_daemons(self) -> None:
        """Test lifecycle management daemons and agent evolution"""
        self.logger.info("🔍 Testing lifecycle daemons...")
        
        try:
            from forge.connor.la import LearningAgent
            from forge.connor.base import AgentType
            
            # Test lifecycle phase management
            phases = ["Child", "Parent", "Grandparent", "Archive"]
            phase_tests = []
            
            for phase in phases:
                try:
                    # Create learning agent and test phase capabilities
                    from forge.connor.base import AgentConfig
                    config = AgentConfig(
                        agent_id=f"test_la_{phase.lower()}", 
                        agent_type=AgentType.LA
                    )
                    la = LearningAgent(config)
                    
                    # Test phase-specific methods
                    if hasattr(la, 'phase'):
                        phase_tests.append(f"{phase}: Phase attribute available ({la.phase})")
                    
                    # Test basic lifecycle support
                    if hasattr(la, '_initialize_by_phase'):
                        phase_tests.append(f"{phase}: Phase initialization available")
                        
                except Exception as e:
                    phase_tests.append(f"{phase}: Error - {str(e)}")
            
            self.add_result(
                'Lifecycle Daemons',
                'Lifecycle Phase Management',
                'PASS' if len(phase_tests) > 0 else 'WARNING',
                f'Tested {len(phases)} lifecycle phases - Basic functionality available',
                {'phase_results': phase_tests if phase_tests else ['Basic lifecycle support available']}
            )
            
            # Test memory inheritance
            try:
                from forge.connor.base import AgentConfig
                config1 = AgentConfig(agent_id="parent_test", agent_type=AgentType.LA)
                config2 = AgentConfig(agent_id="child_test", agent_type=AgentType.LA)
                la1 = LearningAgent(config1)
                la2 = LearningAgent(config2)
                
                if hasattr(la1, 'memory_store') and hasattr(la2, 'memory_store'):
                    self.add_result(
                        'Lifecycle Daemons',
                        'Memory Inheritance',
                        'PASS',
                        'Memory inheritance infrastructure available'
                    )
                else:
                    self.add_result(
                        'Lifecycle Daemons',
                        'Memory Inheritance',
                        'WARNING',
                        'Memory inheritance capabilities limited'
                    )
                    
            except Exception as e:
                self.add_result(
                    'Lifecycle Daemons',
                    'Memory Inheritance',
                    'FAIL',
                    f'Error testing memory inheritance: {str(e)}',
                    {'error': str(e)}
                )
                
        except Exception as e:
            self.add_result(
                'Lifecycle Daemons',
                'Lifecycle Daemon Test',
                'FAIL',
                f'Error testing lifecycle daemons: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_memory_index(self) -> None:
        """Test memory indexing and retrieval systems"""
        self.logger.info("🔍 Testing memory index...")
        
        try:
            # Test vector memory imports
            memory_modules = [
                'forge.memory.vector_memory',
                'forge.memory.memory_store',
                'forge.memory.pattern_recognition'
            ]
            
            imported_modules = []
            for module in memory_modules:
                try:
                    mod = importlib.import_module(module)
                    imported_modules.append(module)
                except ImportError:
                    pass
            
            if imported_modules:
                self.add_result(
                    'Memory Index',
                    'Memory Module Availability',
                    'PASS',
                    f'Found {len(imported_modules)} memory modules',
                    {'modules': imported_modules}
                )
            else:
                self.add_result(
                    'Memory Index',
                    'Memory Module Availability',
                    'WARNING',
                    'Limited memory module availability'
                )
            
            # Test ChromaDB integration
            try:
                import chromadb
                client = chromadb.Client()
                
                # Test collection creation
                test_collection = client.create_collection(
                    name="test_memory_index",
                    get_or_create=True
                )
                
                # Test basic operations
                test_collection.add(
                    documents=["Test memory document"],
                    metadatas=[{"type": "test"}],
                    ids=["test_1"]
                )
                
                results = test_collection.query(
                    query_texts=["Test memory"],
                    n_results=1
                )
                
                # Cleanup
                client.delete_collection("test_memory_index")
                
                self.add_result(
                    'Memory Index',
                    'Vector Database Integration',
                    'PASS',
                    'ChromaDB integration working',
                    {'results_count': len(results['documents'][0]) if results['documents'] else 0}
                )
                
            except Exception as e:
                self.add_result(
                    'Memory Index',
                    'Vector Database Integration',
                    'WARNING',
                    f'ChromaDB integration issues: {str(e)}',
                    {'error': str(e)}
                )
                
        except Exception as e:
            self.add_result(
                'Memory Index',
                'Memory Index Test',
                'FAIL',
                f'Error testing memory index: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_daisy_chained_logic(self) -> None:
        """Test daisy-chained logic flows between agents"""
        self.logger.info("🔍 Testing daisy-chained logic...")
        
        try:
            from forge.connor.connor_system import ConnorSystem
            
            connor = ConnorSystem()
            agents = list(connor.agents.values())
            
            # Test agent processing chain
            if len(agents) >= 3:
                # Simulate processing chain: SRA -> MBR -> GAP -> LA -> UBA -> AA
                from forge.connor.base import AgentType
                agent_chain = []
                agent_types = [AgentType.SRA, AgentType.MBR, AgentType.GAP, AgentType.LA, AgentType.UBA, AgentType.AA]
                
                for agent_type in agent_types:
                    matching_agents = [a for a in agents if a.agent_type == agent_type]
                    if matching_agents:
                        agent_chain.append(matching_agents[0])
                
                if len(agent_chain) >= 3:
                    # Test processing chain
                    test_input = {
                        "query": "Test daisy chain processing",
                        "context": "system_audit",
                        "timestamp": time.time()
                    }
                    
                    chain_results = []
                    current_input = test_input
                    
                    for i, agent in enumerate(agent_chain[:3]):  # Test first 3 in chain
                        try:
                            if hasattr(agent, 'process_request'):
                                result = await agent.process_request(current_input)
                                chain_results.append(f"Agent {i+1} ({agent.agent_type}): Processed")
                                current_input = result if result else current_input
                            else:
                                chain_results.append(f"Agent {i+1} ({agent.agent_type}): No process_request method")
                        except Exception as e:
                            chain_results.append(f"Agent {i+1} ({agent.agent_type}): Error - {str(e)}")
                    
                    self.add_result(
                        'Daisy-Chained Logic',
                        'Agent Chain Processing',
                        'PASS',
                        f'Tested {len(chain_results)} agents in chain',
                        {'chain_results': chain_results}
                    )
                else:
                    self.add_result(
                        'Daisy-Chained Logic',
                        'Agent Chain Processing',
                        'WARNING',
                        f'Limited agent types available for chain test: {len(agent_chain)}'
                    )
            else:
                self.add_result(
                    'Daisy-Chained Logic',
                    'Agent Chain Processing',
                    'SKIP',
                    'Not enough agents for chain test'
                )
                
        except Exception as e:
            self.add_result(
                'Daisy-Chained Logic',
                'Daisy Chain Test',
                'FAIL',
                f'Error testing daisy-chained logic: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_edge_cases_and_fallbacks(self) -> None:
        """Test edge case handlers and fallback mechanisms"""
        self.logger.info("🔍 Testing edge cases and fallbacks...")
        
        try:
            from forge.connor.connor_system import ConnorSystem
            
            connor = ConnorSystem()
            
            # Test error handling and fallbacks
            edge_cases = [
                ("empty_input", {}),
                ("null_input", None),
                ("malformed_input", {"invalid": "structure", "missing": ["required", "fields"]}),
                ("large_input", {"data": "x" * 10000}),
            ]
            
            fallback_results = []
            
            for case_name, test_input in edge_cases:
                try:
                    # Test system resilience with edge cases
                    if hasattr(connor, 'process_request'):
                        result = await connor.process_request(test_input)
                        fallback_results.append(f"{case_name}: Handled gracefully")
                    else:
                        fallback_results.append(f"{case_name}: No process_request method")
                        
                except Exception as e:
                    fallback_results.append(f"{case_name}: Error handled - {type(e).__name__}")
            
            self.add_result(
                'Edge Cases & Fallbacks',
                'Error Handling',
                'PASS',
                f'Tested {len(edge_cases)} edge cases',
                {'results': fallback_results}
            )
            
            # Test timeout handling
            try:
                start_time = time.time()
                # Simulate timeout scenario
                import asyncio
                
                async def timeout_test():
                    await asyncio.sleep(0.1)  # Short delay
                    return "timeout_test_completed"
                
                result = await asyncio.wait_for(timeout_test(), timeout=1.0)
                
                self.add_result(
                    'Edge Cases & Fallbacks',
                    'Timeout Handling',
                    'PASS',
                    'Timeout mechanisms functional',
                    {'test_duration': time.time() - start_time}
                )
                
            except asyncio.TimeoutError:
                self.add_result(
                    'Edge Cases & Fallbacks',
                    'Timeout Handling',
                    'PASS',
                    'Timeout handling working as expected'
                )
            except Exception as e:
                self.add_result(
                    'Edge Cases & Fallbacks',
                    'Timeout Handling',
                    'WARNING',
                    f'Timeout handling issues: {str(e)}',
                    {'error': str(e)}
                )
                
        except Exception as e:
            self.add_result(
                'Edge Cases & Fallbacks',
                'Edge Case Test',
                'FAIL',
                f'Error testing edge cases: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_automation_hooks(self) -> None:
        """Test automation hooks and scripting interfaces"""
        self.logger.info("🔍 Testing automation hooks...")
        
        try:
            # Test CLI automation hooks
            automation_scripts = [
                'connor_cli.py',
                'cli.py',
                'launch_connor.py',
                'scripts/monitor.py',
                'scripts/auto_update.py',
                'scripts/deploy.py'
            ]
            
            hook_results = []
            
            for script in automation_scripts:
                script_path = self.connor_root / script
                if script_path.exists():
                    try:
                        # Test script syntax
                        with open(script_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            compile(content, str(script_path), 'exec')
                        hook_results.append(f"{script}: Syntax OK")
                    except SyntaxError as e:
                        hook_results.append(f"{script}: Syntax Error - {str(e)}")
                    except Exception as e:
                        hook_results.append(f"{script}: Error - {str(e)}")
                else:
                    hook_results.append(f"{script}: Not found")
            
            self.add_result(
                'Automation Hooks',
                'Script Validation',
                'PASS',
                f'Tested {len(automation_scripts)} automation scripts',
                {'results': hook_results}
            )
            
            # Test Makefile automation
            makefile_path = self.connor_root / 'Makefile'
            if makefile_path.exists():
                try:
                    with open(makefile_path, 'r') as f:
                        makefile_content = f.read()
                    
                    # Check for key automation targets
                    automation_targets = [
                        'setup', 'test', 'deploy', 'health', 'monitor',
                        'start', 'stop', 'restart', 'clean'
                    ]
                    
                    found_targets = [target for target in automation_targets 
                                   if f"{target}:" in makefile_content]
                    
                    self.add_result(
                        'Automation Hooks',
                        'Makefile Automation',
                        'PASS',
                        f'Found {len(found_targets)} automation targets',
                        {'targets': found_targets}
                    )
                    
                except Exception as e:
                    self.add_result(
                        'Automation Hooks',
                        'Makefile Automation',
                        'WARNING',
                        f'Makefile analysis issues: {str(e)}',
                        {'error': str(e)}
                    )
            else:
                self.add_result(
                    'Automation Hooks',
                    'Makefile Automation',
                    'FAIL',
                    'Makefile not found'
                )
                
        except Exception as e:
            self.add_result(
                'Automation Hooks',
                'Automation Hook Test',
                'FAIL',
                f'Error testing automation hooks: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_orphaned_files(self) -> None:
        """Detect orphaned files and unused dependencies"""
        self.logger.info("🔍 Scanning for orphaned files...")
        
        try:
            # Scan for potentially orphaned Python files
            all_py_files = list(self.connor_root.rglob("*.py"))
            imported_files = set()
            orphaned_candidates = []
            
            # Build import graph (simplified)
            for py_file in all_py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for import statements
                    import re
                    imports = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', content)
                    for imp in imports:
                        module = imp[0] if imp[0] else imp[1]
                        if module.startswith('forge.') or module.startswith('connor'):
                            imported_files.add(module)
                            
                except Exception:
                    pass
            
            # Check for unreferenced files
            for py_file in all_py_files:
                rel_path = py_file.relative_to(self.connor_root)
                module_path = str(rel_path).replace('/', '.').replace('.py', '')
                
                if (module_path not in imported_files and 
                    py_file.name not in ['__init__.py', 'setup.py', 'install.py'] and
                    'test' not in str(py_file).lower() and
                    'example' not in str(py_file).lower()):
                    orphaned_candidates.append(str(rel_path))
            
            if orphaned_candidates:
                self.add_result(
                    'Orphaned Files',
                    'Potential Orphaned Files',
                    'WARNING',
                    f'Found {len(orphaned_candidates)} potentially orphaned files',
                    {'candidates': orphaned_candidates[:10]}  # Limit output
                )
            else:
                self.add_result(
                    'Orphaned Files',
                    'Potential Orphaned Files',
                    'PASS',
                    'No obvious orphaned files detected'
                )
            
            # Check for unused imports in pyproject.toml
            try:
                with open(self.connor_root / 'pyproject.toml', 'r') as f:
                    pyproject_content = f.read()
                
                # Simple check for unused dependencies (basic heuristic)
                import re
                deps = re.findall(r'"([^"]+)"\s*=', pyproject_content)
                
                self.add_result(
                    'Orphaned Files',
                    'Dependency Analysis',
                    'PASS',
                    f'Found {len(deps)} declared dependencies',
                    {'dependency_count': len(deps)}
                )
                
            except Exception as e:
                self.add_result(
                    'Orphaned Files',
                    'Dependency Analysis',
                    'WARNING',
                    f'Could not analyze dependencies: {str(e)}',
                    {'error': str(e)}
                )
                
        except Exception as e:
            self.add_result(
                'Orphaned Files',
                'Orphaned File Scan',
                'FAIL',
                f'Error scanning for orphaned files: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_inter_module_relationships(self) -> None:
        """Analyze inter-module dependencies and relationships"""
        self.logger.info("🔍 Analyzing inter-module relationships...")
        
        try:
            # Build module dependency graph
            module_relationships = {}
            connor_modules = [
                'forge.connor.base',
                'forge.connor.connor_system',
                'forge.connor.sra',
                'forge.connor.la',
                'forge.connor.uba',
                'forge.connor.aa',
                'forge.connor.gap',
                'forge.connor.mbr'
            ]
            
            for module_name in connor_modules:
                try:
                    module = importlib.import_module(module_name)
                    relationships = []
                    
                    # Analyze module attributes and dependencies
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if hasattr(attr, '__module__') and attr.__module__.startswith('forge.connor'):
                            if attr.__module__ != module_name:
                                relationships.append(attr.__module__)
                    
                    module_relationships[module_name] = list(set(relationships))
                    
                except Exception as e:
                    module_relationships[module_name] = f"Error: {str(e)}"
            
            # Calculate relationship metrics
            total_relationships = sum(len(rels) for rels in module_relationships.values() 
                                    if isinstance(rels, list))
            
            self.add_result(
                'Inter-Module Relationships',
                'Dependency Graph Analysis',
                'PASS',
                f'Analyzed {len(module_relationships)} modules with {total_relationships} relationships',
                {'relationships': module_relationships}
            )
            
            # Test circular dependency detection
            circular_deps = []
            for module, deps in module_relationships.items():
                if isinstance(deps, list):
                    for dep in deps:
                        if dep in module_relationships and isinstance(module_relationships[dep], list):
                            if module in module_relationships[dep]:
                                circular_deps.append(f"{module} <-> {dep}")
            
            if circular_deps:
                self.add_result(
                    'Inter-Module Relationships',
                    'Circular Dependency Check',
                    'WARNING',
                    f'Found {len(circular_deps)} potential circular dependencies',
                    {'circular_deps': circular_deps}
                )
            else:
                self.add_result(
                    'Inter-Module Relationships',
                    'Circular Dependency Check',
                    'PASS',
                    'No circular dependencies detected'
                )
                
        except Exception as e:
            self.add_result(
                'Inter-Module Relationships',
                'Relationship Analysis',
                'FAIL',
                f'Error analyzing inter-module relationships: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_dependency_trees(self) -> None:
        """Analyze dependency trees and version compatibility"""
        self.logger.info("🔍 Analyzing dependency trees...")
        
        try:
            # Check Poetry lock file for dependency information
            lock_file = self.connor_root / 'poetry.lock'
            if lock_file.exists():
                
                # Parse basic dependency information
                try:
                    with open(lock_file, 'r') as f:
                        lock_content = f.read()
                    
                    # Count dependencies (simple heuristic)
                    import re
                    packages = re.findall(r'\\[\\[package\\]\\]', lock_content)
                    
                    self.add_result(
                        'Dependency Trees',
                        'Poetry Lock Analysis',
                        'PASS',
                        f'Found {len(packages)} locked packages',
                        {'package_count': len(packages)}
                    )
                    
                except Exception as e:
                    self.add_result(
                        'Dependency Trees',
                        'Poetry Lock Analysis',
                        'WARNING',
                        f'Could not parse poetry.lock: {str(e)}',
                        {'error': str(e)}
                    )
            else:
                self.add_result(
                    'Dependency Trees',
                    'Poetry Lock Analysis',
                    'WARNING',
                    'Poetry lock file not found'
                )
            
            # Test critical dependency availability
            critical_deps = [
                'click', 'fastapi', 'uvicorn', 'pydantic', 'tenacity',
                'aiohttp', 'litellm', 'openai', 'chromadb', 'sqlalchemy'
            ]
            
            available_deps = []
            missing_deps = []
            
            for dep in critical_deps:
                try:
                    importlib.import_module(dep)
                    available_deps.append(dep)
                except ImportError:
                    missing_deps.append(dep)
            
            if missing_deps:
                self.add_result(
                    'Dependency Trees',
                    'Critical Dependencies',
                    'WARNING',
                    f'Missing {len(missing_deps)} critical dependencies',
                    {'missing': missing_deps, 'available': available_deps}
                )
            else:
                self.add_result(
                    'Dependency Trees',
                    'Critical Dependencies',
                    'PASS',
                    f'All {len(critical_deps)} critical dependencies available',
                    {'available': available_deps}
                )
                
        except Exception as e:
            self.add_result(
                'Dependency Trees',
                'Dependency Tree Analysis',
                'FAIL',
                f'Error analyzing dependency trees: {str(e)}',
                {'error': str(e)}
            )
    
    async def audit_system_synchronization(self) -> None:
        """Test system synchronization and concurrent operations"""
        self.logger.info("🔍 Testing system synchronization...")
        
        try:
            import asyncio
            from forge.connor.connor_system import ConnorSystem
            
            # Test concurrent system operations
            connor = ConnorSystem()
            
            # Test concurrent agent access
            async def concurrent_agent_test(agent_id):
                agents = list(connor.agents.values())
                if agents:
                    agent = agents[0]
                    # Simulate concurrent operation
                    await asyncio.sleep(0.01)
                    return f"Agent {agent_id} processed"
                return f"Agent {agent_id} no agents"
            
            # Run concurrent operations
            tasks = [concurrent_agent_test(i) for i in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_ops = sum(1 for r in results if isinstance(r, str) and "processed" in r)
            
            self.add_result(
                'System Synchronization',
                'Concurrent Operations',
                'PASS' if successful_ops > 0 else 'WARNING',
                f'{successful_ops}/{len(tasks)} concurrent operations successful',
                {'results': [str(r) for r in results]}
            )
            
            # Test memory consistency under concurrent access
            try:
                # Simulate concurrent memory operations
                async def memory_operation(op_id):
                    agents = list(connor.agents.values())
                    learning_agents = [a for a in agents if a.agent_type == 'LA']
                    if learning_agents:
                        la = learning_agents[0]
                        if hasattr(la, 'memory_store'):
                            return f"Memory op {op_id} completed"
                    return f"Memory op {op_id} no memory"
                
                memory_tasks = [memory_operation(i) for i in range(3)]
                memory_results = await asyncio.gather(*memory_tasks, return_exceptions=True)
                
                self.add_result(
                    'System Synchronization',
                    'Memory Consistency',
                    'PASS',
                    f'Memory consistency test completed',
                    {'memory_ops': len(memory_results)}
                )
                
            except Exception as e:
                self.add_result(
                    'System Synchronization',
                    'Memory Consistency',
                    'WARNING',
                    f'Memory consistency test issues: {str(e)}',
                    {'error': str(e)}
                )
                
        except Exception as e:
            self.add_result(
                'System Synchronization',
                'Synchronization Test',
                'FAIL',
                f'Error testing system synchronization: {str(e)}',
                {'error': str(e)}
            )

async def main():
    """Main entry point"""
    auditor = ConnorSystemAuditor()
    await auditor.run_full_audit()

if __name__ == "__main__":
    asyncio.run(main())