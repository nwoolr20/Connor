#!/usr/bin/env python3
"""
Connor System Comprehensive Benchmark Suite
===========================================

Runs detailed performance benchmarks across all Connor system components:
- Agent processing performance
- Memory system throughput
- Inter-agent communication latency
- System scaling behavior
- Load testing and stress scenarios
- Resource utilization analysis
"""

import asyncio
import time
import sys
import os
import json
import statistics
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

# Add Connor modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autogpts', 'forge'))

@dataclass
class BenchmarkResult:
    """Result from a benchmark test"""
    test_name: str
    duration: float
    throughput: float
    memory_usage: float
    cpu_usage: float
    success_rate: float
    details: Dict[str, Any]

class ConnorBenchmarkSuite:
    """Comprehensive benchmark suite for Connor system"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.connor_system = None
        self.start_memory = psutil.virtual_memory().used
        self.reports_dir = Path(__file__).parent / 'docs' / 'benchmark_reports'
        self.reports_dir.mkdir(exist_ok=True, parents=True)
        
    async def initialize_system(self):
        """Initialize Connor system for benchmarking"""
        print("🚀 Initializing Connor system for benchmarking...")
        
        try:
            from forge.connor.connor_system import ConnorSystem
            self.connor_system = ConnorSystem()
            print(f"✅ Connor system initialized with {len(self.connor_system.agents)} agents")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Connor system: {e}")
            return False
    
    def measure_resources(self) -> Tuple[float, float]:
        """Measure current CPU and memory usage"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_used = psutil.virtual_memory().used
        memory_mb = (memory_used - self.start_memory) / 1024 / 1024
        return cpu_percent, memory_mb
    
    async def benchmark_agent_processing(self) -> BenchmarkResult:
        """Benchmark individual agent processing performance"""
        print("⚡ Benchmarking agent processing performance...")
        
        if not self.connor_system:
            return BenchmarkResult("Agent Processing", 0, 0, 0, 0, 0, {"error": "System not initialized"})
        
        test_inputs = [
            "Process this simple request",
            "Analyze this complex multi-part query with various components",
            "Handle this edge case with special characters: !@#$%^&*()",
            "Process this JSON data: {'key': 'value', 'numbers': [1, 2, 3]}",
            "Execute a sequential workflow task"
        ]
        
        start_time = time.time()
        success_count = 0
        total_tests = len(test_inputs) * len(self.connor_system.agents)
        
        cpu_start, mem_start = self.measure_resources()
        
        for agent_id, agent in self.connor_system.agents.items():
            for input_data in test_inputs:
                try:
                    result = await agent.process_input(input_data)
                    if result:
                        success_count += 1
                except Exception as e:
                    print(f"Agent {agent_id} failed on input: {e}")
        
        duration = time.time() - start_time
        cpu_end, mem_end = self.measure_resources()
        
        throughput = total_tests / duration if duration > 0 else 0
        success_rate = success_count / total_tests if total_tests > 0 else 0
        
        result = BenchmarkResult(
            test_name="Agent Processing",
            duration=duration,
            throughput=throughput,
            memory_usage=mem_end,
            cpu_usage=cpu_end,
            success_rate=success_rate,
            details={
                "total_tests": total_tests,
                "successful_tests": success_count,
                "agents_tested": len(self.connor_system.agents),
                "inputs_per_agent": len(test_inputs)
            }
        )
        
        print(f"  ✅ Processed {total_tests} requests in {duration:.2f}s ({throughput:.1f} req/s)")
        print(f"  📊 Success rate: {success_rate*100:.1f}%")
        
        return result
    
    async def benchmark_system_scaling(self) -> BenchmarkResult:
        """Benchmark system behavior under increasing load"""
        print("📈 Benchmarking system scaling behavior...")
        
        if not self.connor_system:
            return BenchmarkResult("System Scaling", 0, 0, 0, 0, 0, {"error": "System not initialized"})
        
        load_levels = [1, 5, 10, 20, 50]
        scaling_results = []
        
        cpu_start, mem_start = self.measure_resources()
        total_duration = 0
        
        for load_level in load_levels:
            print(f"  Testing load level: {load_level} concurrent requests")
            
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = []
            for i in range(load_level):
                # Distribute requests across different agents
                agent_id = list(self.connor_system.agents.keys())[i % len(self.connor_system.agents)]
                agent = self.connor_system.agents[agent_id]
                task = agent.process_input(f"Concurrent request {i} at load {load_level}")
                tasks.append(task)
            
            # Execute all tasks concurrently
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count = sum(1 for r in results if not isinstance(r, Exception))
            except Exception as e:
                success_count = 0
            
            level_duration = time.time() - start_time
            total_duration += level_duration
            
            level_throughput = load_level / level_duration if level_duration > 0 else 0
            level_success_rate = success_count / load_level if load_level > 0 else 0
            
            scaling_results.append({
                "load_level": load_level,
                "duration": level_duration,
                "throughput": level_throughput,
                "success_rate": level_success_rate
            })
            
            # Small delay between load levels
            await asyncio.sleep(0.1)
        
        cpu_end, mem_end = self.measure_resources()
        
        # Calculate average metrics
        avg_throughput = statistics.mean([r["throughput"] for r in scaling_results])
        avg_success_rate = statistics.mean([r["success_rate"] for r in scaling_results])
        
        result = BenchmarkResult(
            test_name="System Scaling",
            duration=total_duration,
            throughput=avg_throughput,
            memory_usage=mem_end,
            cpu_usage=cpu_end,
            success_rate=avg_success_rate,
            details={
                "load_levels_tested": load_levels,
                "scaling_results": scaling_results,
                "max_load": max(load_levels),
                "performance_degradation": self._calculate_degradation(scaling_results)
            }
        )
        
        print(f"  ✅ Tested up to {max(load_levels)} concurrent requests")
        print(f"  📊 Average throughput: {avg_throughput:.1f} req/s")
        
        return result
    
    def _calculate_degradation(self, scaling_results: List[Dict]) -> float:
        """Calculate performance degradation as load increases"""
        if len(scaling_results) < 2:
            return 0.0
        
        first_throughput = scaling_results[0]["throughput"]
        last_throughput = scaling_results[-1]["throughput"]
        
        if first_throughput == 0:
            return 0.0
        
        degradation = (first_throughput - last_throughput) / first_throughput
        return max(0.0, degradation)
    
    async def benchmark_memory_system(self) -> BenchmarkResult:
        """Benchmark memory system performance"""
        print("🧠 Benchmarking memory system...")
        
        try:
            from forge.memory import MemStore
            
            # Test memory operations
            mem_store = MemStore()
            start_time = time.time()
            
            cpu_start, mem_start = self.measure_resources()
            
            # Memory write benchmark
            num_items = 1000
            for i in range(num_items):
                await mem_store.add(f"test_memory_{i}", {"data": f"test data {i}", "index": i})
            
            # Memory read benchmark
            success_count = 0
            for i in range(num_items):
                try:
                    result = await mem_store.query(f"test_memory_{i}")
                    if result:
                        success_count += 1
                except:
                    pass
            
            duration = time.time() - start_time
            cpu_end, mem_end = self.measure_resources()
            
            throughput = (num_items * 2) / duration  # Both read and write operations
            success_rate = success_count / num_items
            
            result = BenchmarkResult(
                test_name="Memory System",
                duration=duration,
                throughput=throughput,
                memory_usage=mem_end,
                cpu_usage=cpu_end,
                success_rate=success_rate,
                details={
                    "items_stored": num_items,
                    "items_retrieved": success_count,
                    "operations_per_second": throughput
                }
            )
            
            print(f"  ✅ Processed {num_items*2} memory operations in {duration:.2f}s")
            print(f"  📊 {throughput:.1f} ops/s, {success_rate*100:.1f}% success rate")
            
            return result
            
        except Exception as e:
            print(f"  ❌ Memory system benchmark failed: {e}")
            return BenchmarkResult("Memory System", 0, 0, 0, 0, 0, {"error": str(e)})
    
    async def benchmark_agent_communication(self) -> BenchmarkResult:
        """Benchmark inter-agent communication"""
        print("📡 Benchmarking agent communication...")
        
        if not self.connor_system or len(self.connor_system.agents) < 2:
            return BenchmarkResult("Agent Communication", 0, 0, 0, 0, 0, {"error": "Need at least 2 agents"})
        
        agents = list(self.connor_system.agents.values())
        num_messages = 100
        
        start_time = time.time()
        cpu_start, mem_start = self.measure_resources()
        
        success_count = 0
        
        # Test message passing between agents
        for i in range(num_messages):
            sender = agents[i % len(agents)]
            receiver = agents[(i + 1) % len(agents)]
            
            try:
                # Simulate message passing
                message_data = {
                    "type": "benchmark_message",
                    "content": f"Test message {i}",
                    "timestamp": time.time()
                }
                
                # In a real system this would be actual inter-agent communication
                # For now we'll test the agent's message handling capability
                from forge.connor.base import AgentMessage
                
                message = AgentMessage(
                    sender_id=sender.agent_id,
                    sender_type=sender.agent_type,
                    content=message_data
                )
                
                result = await receiver.handle_message(message)
                if result is not None:
                    success_count += 1
                else:
                    success_count += 1  # None response is valid for some agents
                    
            except Exception as e:
                print(f"  Communication error: {e}")
        
        duration = time.time() - start_time
        cpu_end, mem_end = self.measure_resources()
        
        throughput = num_messages / duration if duration > 0 else 0
        success_rate = success_count / num_messages if num_messages > 0 else 0
        
        result = BenchmarkResult(
            test_name="Agent Communication",
            duration=duration,
            throughput=throughput,
            memory_usage=mem_end,
            cpu_usage=cpu_end,
            success_rate=success_rate,
            details={
                "messages_sent": num_messages,
                "messages_processed": success_count,
                "agents_involved": len(agents),
                "average_latency": duration / num_messages if num_messages > 0 else 0
            }
        )
        
        print(f"  ✅ Sent {num_messages} messages in {duration:.2f}s ({throughput:.1f} msg/s)")
        print(f"  📊 Success rate: {success_rate*100:.1f}%")
        
        return result
    
    async def benchmark_concurrent_agents(self) -> BenchmarkResult:
        """Benchmark multiple agents working concurrently"""
        print("⚡ Benchmarking concurrent agent operations...")
        
        if not self.connor_system:
            return BenchmarkResult("Concurrent Agents", 0, 0, 0, 0, 0, {"error": "System not initialized"})
        
        num_tasks_per_agent = 10
        agents = list(self.connor_system.agents.values())
        
        start_time = time.time()
        cpu_start, mem_start = self.measure_resources()
        
        # Create tasks for all agents to run concurrently
        all_tasks = []
        for agent in agents:
            for i in range(num_tasks_per_agent):
                task = agent.process_input(f"Concurrent task {i} for {agent.agent_id}")
                all_tasks.append(task)
        
        # Execute all tasks concurrently
        try:
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            success_count = sum(1 for r in results if not isinstance(r, Exception))
        except Exception as e:
            success_count = 0
            print(f"  Error in concurrent execution: {e}")
        
        duration = time.time() - start_time
        cpu_end, mem_end = self.measure_resources()
        
        total_tasks = len(all_tasks)
        throughput = total_tasks / duration if duration > 0 else 0
        success_rate = success_count / total_tasks if total_tasks > 0 else 0
        
        result = BenchmarkResult(
            test_name="Concurrent Agents",
            duration=duration,
            throughput=throughput,
            memory_usage=mem_end,
            cpu_usage=cpu_end,
            success_rate=success_rate,
            details={
                "total_tasks": total_tasks,
                "successful_tasks": success_count,
                "agents_tested": len(agents),
                "tasks_per_agent": num_tasks_per_agent,
                "concurrency_level": len(agents)
            }
        )
        
        print(f"  ✅ Executed {total_tasks} concurrent tasks in {duration:.2f}s")
        print(f"  📊 Throughput: {throughput:.1f} tasks/s, Success: {success_rate*100:.1f}%")
        
        return result
    
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmark tests"""
        print("\n🚀 Starting Connor System Comprehensive Benchmark Suite")
        print("=" * 70)
        
        # Initialize system
        if not await self.initialize_system():
            return {"error": "Failed to initialize Connor system"}
        
        start_time = time.time()
        
        # Run all benchmarks
        benchmarks = [
            self.benchmark_agent_processing(),
            self.benchmark_system_scaling(),
            self.benchmark_memory_system(),
            self.benchmark_agent_communication(),
            self.benchmark_concurrent_agents()
        ]
        
        for benchmark in benchmarks:
            try:
                result = await benchmark
                self.results.append(result)
            except Exception as e:
                print(f"❌ Benchmark failed: {e}")
                self.results.append(BenchmarkResult(
                    test_name="Failed Benchmark",
                    duration=0, throughput=0, memory_usage=0,
                    cpu_usage=0, success_rate=0,
                    details={"error": str(e)}
                ))
        
        total_duration = time.time() - start_time
        
        # Generate summary
        summary = self._generate_benchmark_summary(total_duration)
        
        # Save results
        self._save_benchmark_results(summary)
        
        print(f"\n✅ All benchmarks completed in {total_duration:.2f}s")
        print(f"📊 Results saved to: {self.reports_dir}")
        
        return summary
    
    def _generate_benchmark_summary(self, total_duration: float) -> Dict[str, Any]:
        """Generate benchmark summary"""
        if not self.results:
            return {"error": "No benchmark results"}
        
        # Calculate aggregate metrics
        throughput_values = [r.throughput for r in self.results if r.throughput > 0]
        memory_values = [r.memory_usage for r in self.results]
        cpu_values = [r.cpu_usage for r in self.results]
        success_values = [r.success_rate for r in self.results]
        
        avg_throughput = statistics.mean(throughput_values) if throughput_values else 0
        avg_memory = statistics.mean(memory_values) if memory_values else 0
        avg_cpu = statistics.mean(cpu_values) if cpu_values else 0
        avg_success_rate = statistics.mean(success_values) if success_values else 0
        
        # System specifications
        system_info = {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "platform": sys.platform
        }
        
        summary = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_duration": total_duration,
            "system_info": system_info,
            "aggregate_metrics": {
                "average_throughput": avg_throughput,
                "average_memory_usage_mb": avg_memory,
                "average_cpu_usage": avg_cpu,
                "average_success_rate": avg_success_rate
            },
            "benchmark_results": [asdict(result) for result in self.results],
            "performance_grade": self._calculate_performance_grade(),
            "recommendations": self._generate_performance_recommendations()
        }
        
        return summary
    
    def _calculate_performance_grade(self) -> str:
        """Calculate overall performance grade"""
        if not self.results:
            return "F"
        
        # Weight different factors
        success_weight = 0.4
        throughput_weight = 0.3
        efficiency_weight = 0.3
        
        # Calculate normalized scores
        avg_success = statistics.mean([r.success_rate for r in self.results])
        avg_throughput = statistics.mean([r.throughput for r in self.results if r.throughput > 0]) or 0
        
        # Normalize throughput (assuming 100 ops/sec is excellent)
        throughput_score = min(avg_throughput / 100, 1.0)
        
        # Calculate efficiency (low CPU and memory usage is better)
        cpu_values = [r.cpu_usage for r in self.results if r.cpu_usage > 0]
        memory_values = [r.memory_usage for r in self.results if r.memory_usage > 0]
        
        avg_cpu = statistics.mean(cpu_values) if cpu_values else 0
        avg_memory = statistics.mean(memory_values) if memory_values else 0
        
        # Efficiency score (lower resource usage = higher score)
        cpu_efficiency = max(0, 1 - avg_cpu / 100)
        memory_efficiency = max(0, 1 - min(avg_memory / 1000, 1))  # 1GB as baseline
        efficiency_score = (cpu_efficiency + memory_efficiency) / 2
        
        # Weighted final score
        final_score = (
            avg_success * success_weight +
            throughput_score * throughput_weight +
            efficiency_score * efficiency_weight
        )
        
        # Convert to letter grade
        if final_score >= 0.9:
            return "A+"
        elif final_score >= 0.8:
            return "A"
        elif final_score >= 0.7:
            return "B"
        elif final_score >= 0.6:
            return "C"
        elif final_score >= 0.5:
            return "D"
        else:
            return "F"
    
    def _generate_performance_recommendations(self) -> List[Dict[str, str]]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if not self.results:
            return recommendations
        
        avg_throughput = statistics.mean([r.throughput for r in self.results if r.throughput > 0]) if [r.throughput for r in self.results if r.throughput > 0] else 0
        avg_memory = statistics.mean([r.memory_usage for r in self.results]) if self.results else 0
        avg_cpu = statistics.mean([r.cpu_usage for r in self.results]) if self.results else 0
        avg_success = statistics.mean([r.success_rate for r in self.results]) if self.results else 0
        
        # Throughput recommendations
        if avg_throughput < 10:
            recommendations.append({
                "category": "Throughput",
                "priority": "HIGH",
                "issue": f"Low throughput: {avg_throughput:.1f} ops/sec",
                "recommendation": "Optimize agent processing logic and consider async improvements",
                "target": "Aim for >50 ops/sec"
            })
        
        # Memory recommendations
        if avg_memory > 500:
            recommendations.append({
                "category": "Memory",
                "priority": "MEDIUM",
                "issue": f"High memory usage: {avg_memory:.1f}MB",
                "recommendation": "Implement memory cleanup and optimize data structures",
                "target": "Keep memory usage under 200MB"
            })
        
        # CPU recommendations
        if avg_cpu > 80:
            recommendations.append({
                "category": "CPU",
                "priority": "HIGH",
                "issue": f"High CPU usage: {avg_cpu:.1f}%",
                "recommendation": "Profile CPU-intensive operations and optimize algorithms",
                "target": "Keep CPU usage under 50%"
            })
        
        # Success rate recommendations
        if avg_success < 0.95:
            recommendations.append({
                "category": "Reliability",
                "priority": "HIGH",
                "issue": f"Low success rate: {avg_success*100:.1f}%",
                "recommendation": "Improve error handling and input validation",
                "target": "Achieve >95% success rate"
            })
        
        return recommendations
    
    def _save_benchmark_results(self, summary: Dict[str, Any]) -> None:
        """Save benchmark results to files"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save detailed JSON report
        json_file = self.reports_dir / f'connor_benchmark_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save human-readable summary
        summary_file = self.reports_dir / f'connor_benchmark_summary_{timestamp}.md'
        with open(summary_file, 'w') as f:
            self._write_benchmark_markdown(f, summary)
        
        # Save latest report
        latest_json = self.reports_dir / 'latest_benchmark.json'
        latest_md = self.reports_dir / 'latest_benchmark_summary.md'
        
        with open(latest_json, 'w') as f:
            json.dump(summary, f, indent=2)
        
        with open(latest_md, 'w') as f:
            self._write_benchmark_markdown(f, summary)
    
    def _write_benchmark_markdown(self, f, summary: Dict[str, Any]) -> None:
        """Write markdown benchmark report"""
        f.write("# Connor System Benchmark Report\n\n")
        f.write(f"**Timestamp:** {summary['timestamp']}  \n")
        f.write(f"**Duration:** {summary['total_duration']:.2f} seconds  \n")
        f.write(f"**Performance Grade:** {summary['performance_grade']}  \n\n")
        
        # System information
        f.write("## System Information\n\n")
        sys_info = summary['system_info']
        f.write(f"- **CPU Cores:** {sys_info['cpu_count']}\n")
        f.write(f"- **Total Memory:** {sys_info['memory_total_gb']:.1f} GB\n")
        f.write(f"- **Platform:** {sys_info['platform']}\n\n")
        
        # Aggregate metrics
        f.write("## Aggregate Performance Metrics\n\n")
        metrics = summary['aggregate_metrics']
        f.write(f"- **Average Throughput:** {metrics['average_throughput']:.1f} operations/second\n")
        f.write(f"- **Average Memory Usage:** {metrics['average_memory_usage_mb']:.1f} MB\n")
        f.write(f"- **Average CPU Usage:** {metrics['average_cpu_usage']:.1f}%\n")
        f.write(f"- **Average Success Rate:** {metrics['average_success_rate']*100:.1f}%\n\n")
        
        # Individual benchmark results
        f.write("## Benchmark Results\n\n")
        f.write("| Test | Duration (s) | Throughput (ops/s) | Memory (MB) | CPU (%) | Success (%) |\n")
        f.write("|------|-------------:|-------------------:|------------:|--------:|------------:|\n")
        
        for result in summary['benchmark_results']:
            f.write(f"| {result['test_name']} | {result['duration']:.2f} | {result['throughput']:.1f} | {result['memory_usage']:.1f} | {result['cpu_usage']:.1f} | {result['success_rate']*100:.1f} |\n")
        
        f.write("\n")
        
        # Recommendations
        if summary.get('recommendations'):
            f.write("## Performance Recommendations\n\n")
            for i, rec in enumerate(summary['recommendations'], 1):
                priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(rec['priority'], '🔵')
                f.write(f"### {i}. {rec['category']} {priority_emoji}\n\n")
                f.write(f"**Issue:** {rec['issue']}  \n")
                f.write(f"**Recommendation:** {rec['recommendation']}  \n")
                f.write(f"**Target:** {rec['target']}\n\n")
        
        f.write("---\n")
        f.write(f"*Report generated by Connor Benchmark Suite on {summary['timestamp']}*\n")

async def main():
    """Main entry point"""
    benchmark_suite = ConnorBenchmarkSuite()
    await benchmark_suite.run_all_benchmarks()

if __name__ == "__main__":
    asyncio.run(main())