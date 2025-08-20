# Connor Multi-Agent System - Quick Start Guide

## Overview

This guide will help you get started with the Connor Multi-Agent System, a sophisticated AI framework that processes requests through multiple specialized agents working in coordination.

## Installation

### Prerequisites

- Python 3.8+
- AutoGPT Forge framework
- Required dependencies (see requirements below)

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/nwoolr20/Connor.git
cd Connor
```

2. **Install dependencies**:
```bash
cd autogpts/forge
pip install poetry
poetry install
# Or install required packages manually:
pip install litellm tenacity uvicorn fastapi sqlalchemy
```

3. **Set up environment** (optional):
```bash
cp .env.example .env
# Edit .env with your API keys if using external services
```

## Quick Start

### Option 1: Standalone Connor System

```python
import asyncio
from forge.connor import ConnorSystem

async def main():
    # Initialize the Connor system
    connor = ConnorSystem()
    
    # Process a simple request
    response = await connor.process_input(
        "What is machine learning and how does it work?",
        priority=2  # Normal priority
    )
    
    # Display results
    print("🤖 Connor Response:")
    print(f"Answer: {response['final_answer']}")
    print(f"Confidence: {response['system_confidence']:.1%}")
    print(f"Processing Time: {response['processing_time']:.2f}s")
    
    # Show processing pipeline
    stages = response['processing_stages']
    print("\n📊 Processing Pipeline:")
    print(f"SRA: {stages['sra']['classification']} → {stages['sra']['tags']}")
    print(f"MBR: {stages['mbr']['confidence']:.1%} confidence")
    print(f"GAP: {stages['gap']['plan_steps']} step plan")
    
    # Shutdown system
    await connor.shutdown()

# Run the example
asyncio.run(main())
```

### Option 2: AutoGPT Forge Integration

```python
from forge.connor_agent import ConnorForgeAgent
from forge.sdk import AgentDB, Workspace, TaskRequestBody, StepRequestBody

async def forge_example():
    # Create database and workspace
    database = AgentDB("connor_agent.db")
    workspace = Workspace("./workspace")
    
    # Initialize Connor Forge Agent
    agent = ConnorForgeAgent(database, workspace)
    
    # Create a task
    task = await agent.create_task(
        TaskRequestBody(input="Create a Python web API using Flask")
    )
    
    print(f"📦 Task created: {task.task_id}")
    
    # Execute steps
    step = await agent.execute_step(
        task.task_id, 
        StepRequestBody(input="Start with basic setup")
    )
    
    print(f"✅ Step completed: {step.step_id}")
    print(f"Output: {step.output[:200]}...")
    
    # Continue with follow-up
    if not step.is_last:
        next_step = await agent.execute_step(
            task.task_id,
            StepRequestBody(input="Add user authentication")
        )
        print(f"✅ Next step: {next_step.step_id}")

asyncio.run(forge_example())
```

## Understanding the Agent Types

### Simple Reflex Agents (SRAs)
Handle immediate input processing and classification:

```python
from forge.connor.sra import SimpleReflexAgent
from forge.connor.base import AgentConfig, AgentType

# Create SRA
config = AgentConfig(agent_id="my_sra", agent_type=AgentType.SRA)
sra = SimpleReflexAgent(config)

# Process input
result = await sra.process_input("How do I learn Python programming?")
print(f"Classification: {result['input_type']}")
print(f"Tags: {result['tags']}")
print(f"Quick Response: {result['quick_response']}")
```

### Learning Agents (LAs)
Adaptive agents that improve over time:

```python
from forge.connor.la import LearningAgent
from forge.connor.base import AgentPhase

# Create a child learning agent
config = AgentConfig(
    agent_id="learning_child",
    agent_type=AgentType.LA,
    phase=AgentPhase.CHILD,
    family_id="family_1",
    learning_rate=0.1
)
la = LearningAgent(config)

# Process with learning
result = await la.process_input({
    "original_input": "Explain neural networks",
    "context": {"domain": "AI/ML"}
})

print(f"Phase: {result['phase']}")
print(f"Patterns Applied: {len(result['matching_patterns'])}")
print(f"Learning Confidence: {result['confidence']:.1%}")

# Get learning statistics
stats = la.get_learning_statistics()
print(f"Total Patterns: {stats['pattern_statistics']['total_patterns']}")
```

### Utility-Based Agents (UBAs)
Optimize decisions based on multiple criteria:

```python
from forge.connor.uba import UtilityBasedAgent

# Create UBA
config = AgentConfig(agent_id="optimizer", agent_type=AgentType.UBA)
uba = UtilityBasedAgent(config)

# Process for optimization
result = await uba.process_input({
    "original_input": "Choose the best Python web framework",
    "alternatives": ["Flask", "Django", "FastAPI"],
    "criteria": ["simplicity", "performance", "ecosystem"]
})

print(f"Selected: {result['selected_alternative']}")
print(f"Utility Score: {result['expected_utility']:.3f}")
print(f"Alternatives Considered: {result['alternatives_considered']}")
```

## Working with Families

### Creating Learning Agent Families

```python
async def family_example():
    connor = ConnorSystem()
    
    # Create a new family
    family_id = await connor.create_learning_agent_family()
    print(f"Created family: {family_id}")
    
    # Expand with children
    children = await connor.expand_family(family_id, num_children=3)
    print(f"Added children: {children}")
    
    # Check system status
    status = connor.get_system_status()
    family_details = status['family_details'][family_id]
    print(f"Family size: {family_details['children_count']} children")
    print(f"Apprentices: {family_details['apprentices_count']}")
    
    await connor.shutdown()

asyncio.run(family_example())
```

## Advanced Usage

### Custom Agent Configuration

```python
# Create agents with specific configurations
custom_config = AgentConfig(
    agent_id="custom_la",
    agent_type=AgentType.LA,
    phase=AgentPhase.PARENT,
    max_memory_size=2000,
    learning_rate=0.05,
    family_id="custom_family"
)

# Initialize with custom settings
system_config = {
    "max_agents_per_type": 5,
    "memory_cleanup_interval": 3600,
    "learning_batch_size": 10
}

connor = ConnorSystem(system_config)
```

### Monitoring and Metrics

```python
async def monitoring_example():
    connor = ConnorSystem()
    
    # Process several requests
    requests = [
        "What is Python?",
        "Create a web app",
        "Explain machine learning",
        "Build a REST API"
    ]
    
    for req in requests:
        await connor.process_input(req)
    
    # Get system metrics
    status = connor.get_system_status()
    print(f"Total agents: {status['total_agents']}")
    print(f"Active requests: {status['active_requests']}")
    print(f"Completed requests: {status['completed_requests']}")
    
    metrics = status['system_metrics']
    print(f"Success rate: {metrics['success_rate']:.1%}")
    print(f"Avg processing time: {metrics['avg_processing_time']:.2f}s")
    
    await connor.shutdown()

asyncio.run(monitoring_example())
```

### Error Handling

```python
async def error_handling_example():
    connor = ConnorSystem()
    
    try:
        response = await connor.process_input(
            "Complex request that might fail",
            priority=1
        )
        
        if response['success']:
            print(f"Success: {response['final_answer']}")
        else:
            print(f"Error: {response.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"System error: {e}")
    
    finally:
        await connor.shutdown()

asyncio.run(error_handling_example())
```

## Testing Your Setup

Run the included test to verify everything is working:

```bash
# Simple test without heavy dependencies
python standalone_test.py

# Full test (requires all dependencies)
python test_connor.py
```

Expected output:
```
🚀 Testing Standalone Connor Components
============================================================
✅ All core components working
✅ Processing pipeline functional
✅ Memory management operational
✅ Message system ready
✅ Configuration system working
============================================================
```

## Integration with AutoGPT Forge

### Running as Forge Agent

1. **Start the agent server**:
```bash
cd autogpts/forge
python -m forge.app
```

2. **Access the web interface**:
   - Open browser to `http://localhost:8000`
   - Create tasks and interact with Connor system

3. **API Usage**:
```bash
# Create a task
curl -X POST "http://localhost:8000/ap/v1/agent/tasks" \
     -H "Content-Type: application/json" \
     -d '{"input": "Create a Python calculator app"}'

# Execute step
curl -X POST "http://localhost:8000/ap/v1/agent/tasks/{task_id}/steps" \
     -H "Content-Type: application/json" \
     -d '{"input": "Add advanced mathematical functions"}'
```

## Configuration Options

### Environment Variables

Create a `.env` file for configuration:

```bash
# Optional API keys for enhanced functionality
OPENAI_API_KEY=your_openai_key_here
WOLFRAM_API_KEY=your_wolfram_key_here

# System settings
CONNOR_LOG_LEVEL=INFO
CONNOR_MAX_MEMORY_SIZE=1000
CONNOR_DEFAULT_PRIORITY=3
```

### System Configuration

```python
# Custom system configuration
config = {
    "agent_pool_sizes": {
        "SRA": 3,
        "MBR": 2, 
        "GAP": 2,
        "LA": 4,
        "UBA": 1,
        "AA": 1
    },
    "processing_timeouts": {
        "SRA": 5.0,
        "MBR": 15.0,
        "GAP": 30.0,
        "LA": 10.0,
        "UBA": 20.0,
        "AA": 10.0
    },
    "memory_management": {
        "cleanup_interval": 3600,
        "max_total_memory": 10000,
        "archive_threshold": 0.8
    }
}

connor = ConnorSystem(config)
```

## Best Practices

### 1. Input Formulation
- Be specific and clear in your requests
- Provide context when dealing with complex topics
- Use structured input for better processing

### 2. Priority Management
- Use priority 1 for urgent requests
- Priority 2-3 for normal processing
- Priority 4-5 for background tasks

### 3. Memory Management
- Monitor system memory usage regularly
- Clean up unused families periodically
- Archive important learning patterns

### 4. Error Recovery
- Always include error handling in your code
- Monitor system health metrics
- Implement graceful degradation strategies

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Install missing dependencies
   pip install <missing_package>
   ```

2. **Memory Issues**:
   ```python
   # Reduce memory limits
   config.max_memory_size = 500
   ```

3. **Performance Issues**:
   ```python
   # Adjust agent pool sizes
   connor.agent_pools[AgentType.SRA].extend(new_agents)
   ```

4. **Database Errors**:
   ```bash
   # Reset database
   rm connor_agent.db
   ```

### Getting Help

- Check the full documentation: `CONNOR_DOCUMENTATION.md`
- Run diagnostic tests: `python standalone_test.py`
- Review agent logs for detailed error information
- Check system status: `connor.get_system_status()`

## Next Steps

1. **Explore Advanced Features**: Learning agent families, utility optimization
2. **Integrate External APIs**: Wolfram, OpenAI, custom services
3. **Customize Agents**: Create specialized agent variants
4. **Scale Up**: Deploy across multiple machines
5. **Contribute**: Add new agent types or improve existing ones

## Example Projects

### 1. Personal Assistant
Create a Connor-powered personal assistant that learns your preferences.

### 2. Code Review System
Use Connor agents to analyze and review code submissions.

### 3. Research Assistant
Build a system that helps with academic research and paper writing.

### 4. Business Intelligence
Create analytics and decision support using Connor's optimization capabilities.

---

**Ready to start building with Connor?** Begin with the simple examples above and gradually explore more advanced features as you become familiar with the system!