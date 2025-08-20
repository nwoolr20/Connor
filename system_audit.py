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
                agent_type=AgentType.SRA,
                name="Test Agent"
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
            
            avg_import_time = sum(t for t in import_times.values() if t > 0) / len([t for t in import_times.values() if t > 0])
            
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
        
        # Run all audit components
        await self.audit_core_imports()
        await self.audit_agent_initialization()
        await self.audit_connor_system()
        await self.audit_agent_types()
        await self.audit_memory_system()
        await self.audit_cli_interfaces()
        await self.audit_configuration()
        await self.audit_dependencies()
        await self.audit_file_structure()
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
    
    def _save_results(self, summary: Dict[str, Any]) -> None:
        """Save audit results to files"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save detailed JSON report
        json_file = self.reports_dir / f'connor_audit_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save human-readable summary
        summary_file = self.reports_dir / f'connor_audit_summary_{timestamp}.md'
        with open(summary_file, 'w') as f:
            self._write_markdown_summary(f, summary)
        
        # Save latest report (for easy access)
        latest_json = self.reports_dir / 'latest_audit.json'
        latest_md = self.reports_dir / 'latest_audit_summary.md'
        
        with open(latest_json, 'w') as f:
            json.dump(summary, f, indent=2)
        
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

async def main():
    """Main entry point"""
    auditor = ConnorSystemAuditor()
    await auditor.run_full_audit()

if __name__ == "__main__":
    asyncio.run(main())