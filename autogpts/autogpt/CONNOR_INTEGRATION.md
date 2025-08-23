# Connor-AutoGPT Integration Guide

## Overview

This integration successfully merges Connor's sophisticated multi-agent system with AutoGPT's proven interface, creating a unified AI assistant that combines the best of both worlds.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                         │
│                     (AutoGPT Interface)                        │
├─────────────────────────────────────────────────────────────────┤
│  CLI Commands  │  Web UI  │  Agent Protocol  │  Configuration  │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOGPT FRAMEWORK                           │
│              (Task Management & Execution)                     │
├─────────────────────────────────────────────────────────────────┤
│   Task Parser   │   Workspace   │   Memory   │   File Storage  │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CONNOR MULTI-AGENT SYSTEM                      │
│              (Intelligent Decision Making)                     │
├─────────────────────────────────────────────────────────────────┤
│  SRA  →  MBR  →  GAP  →  LA  →  UBA  →  AA                    │
│  ├─3   ├─2     ├─2     ├─4    ├─1     └─1                      │
│  └─────┴───────┴───────┴──────┴───────────────────────────────── │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      COMMAND EXECUTION                         │
│              (Actions in Real Environment)                     │
├─────────────────────────────────────────────────────────────────┤
│  File Ops  │  Web Access  │  Code Exec  │  API Calls  │  etc.  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. AutoGPT Interface (Preserved)
- **CLI Commands**: All original AutoGPT commands work seamlessly
- **Configuration**: Same configuration files and environment variables
- **Task Management**: AutoGPT's proven task parsing and execution framework
- **File Storage**: Workspace management and file operations
- **Memory System**: Long-term memory and context management

### 2. Connor Multi-Agent System (Integrated)
- **SRA (Simple Reflex Agent)**: 3 agents for immediate response processing
- **MBR (Model-Based Reflex Agent)**: 2 agents for context-aware decisions
- **GAP (Goal-Based Agent-Planner)**: 2 agents for strategic planning
- **LA (Learning Agent)**: 4 agents for pattern recognition and adaptation
- **UBA (Utility-Based Agent)**: 1 agent for optimization decisions
- **AA (Apprentice Agent)**: 1 agent for learning from user interactions

### 3. ConnorAgent Integration
- Replaces AutoGPT's single-agent decision making with Connor's multi-agent pipeline
- Maps Connor's responses to AutoGPT's command format
- Preserves all AutoGPT functionality while enhancing intelligence

## Usage

### Starting the Integrated System

```bash
# Method 1: Using the integrated startup script
cd autogpts/autogpt
./run_connor_autogpt.sh

# Method 2: Using the demo (for testing)
cd autogpts/autogpt
python connor_autogpt_demo.py

# Method 3: Direct Python execution
cd autogpts/autogpt
PYTHONPATH="../forge:." python -m autogpt
```

### AutoGPT Commands with Connor Intelligence

All standard AutoGPT commands now use Connor's multi-agent system:

```bash
# Continuous mode with Connor's multi-agent decision making
./run_connor_autogpt.sh --continuous

# GPT-4 mode optimized by Connor's utility-based agent
./run_connor_autogpt.sh --gpt4only

# Custom AI settings with Connor's adaptive learning
./run_connor_autogpt.sh --ai-name "Connor-Assistant" --ai-role "Multi-Agent AI"
```

## Configuration

### Environment Variables

Create `.env` file based on `.env.connor`:

```env
# Core Configuration
OPENAI_API_KEY=your-openai-api-key
CONNOR_ENABLED=true
AI_NAME=Connor
AI_ROLE=Multi-Agent AI Assistant

# Connor System Settings
CONNOR_AGENT_COUNT=13
CONNOR_SRA_COUNT=3
CONNOR_MBR_COUNT=2  
CONNOR_GAP_COUNT=2
CONNOR_LA_COUNT=4
CONNOR_UBA_COUNT=1
CONNOR_AA_COUNT=1

# Performance Settings
CONNOR_MAX_CONCURRENT_AGENTS=5
CONNOR_PROCESSING_TIMEOUT=30
CONNOR_MEMORY_SIZE=1000
```

### Dependencies

The integration requires additional dependencies:

```bash
pip install litellm chromadb sqlalchemy fastapi uvicorn python-multipart sentry-sdk
```

## How It Works

### 1. User Interaction
- Users interact through AutoGPT's familiar CLI interface
- Commands and tasks are processed by AutoGPT's proven framework
- Configuration and workspace management remain unchanged

### 2. Decision Making
- Instead of AutoGPT's single agent making decisions, the task is passed to Connor's multi-agent system
- Connor's pipeline processes the input through all 6 agent types:
  - **SRA**: Immediate categorization and basic processing
  - **MBR**: Context-aware analysis with memory integration
  - **GAP**: Strategic planning and goal decomposition
  - **LA**: Pattern recognition and adaptive learning
  - **UBA**: Utility optimization and resource allocation
  - **AA**: User interaction learning and personalization

### 3. Command Execution
- Connor's comprehensive analysis is mapped back to AutoGPT command format
- AutoGPT executes the recommended actions using its proven infrastructure
- Results are fed back to Connor for learning and optimization

## Benefits

### For Users
- **Familiar Interface**: No learning curve - same AutoGPT commands and UI
- **Enhanced Intelligence**: Multi-agent decision making instead of single agent
- **Better Results**: Sophisticated analysis leads to more accurate actions
- **Adaptive Behavior**: System learns and improves from interactions

### For Developers
- **Best of Both Worlds**: AutoGPT's mature infrastructure + Connor's AI intelligence
- **Proven Reliability**: AutoGPT's tested task management and execution
- **Advanced AI**: Connor's sophisticated multi-agent reasoning
- **Extensible Architecture**: Easy to add new agents or modify behavior

### For Production
- **Scalable**: Multi-agent system handles complex tasks efficiently
- **Reliable**: Built on AutoGPT's proven foundation
- **Maintainable**: Clear separation between interface and intelligence
- **Configurable**: Extensive settings for different use cases

## Development

### Adding New Agent Types
Connor's architecture makes it easy to add new specialized agents:

```python
# In forge/connor/new_agent.py
class NewSpecializedAgent(BaseConnorAgent):
    async def process_request(self, request: ProcessingRequest) -> Dict[str, Any]:
        # Your specialized logic here
        pass

# Register in connor_system.py
new_agent = NewSpecializedAgent(config)
self.agents[new_agent.agent_id] = new_agent
```

### Customizing AutoGPT Integration
Modify `autogpt/agents/connor_agent.py` to change how Connor's responses are mapped to AutoGPT commands.

### Performance Tuning
Adjust agent counts and processing parameters in configuration files to optimize for your specific use case.

## Testing

Run the integration demo to verify everything works:

```bash
cd autogpts/autogpt
python connor_autogpt_demo.py
```

Expected output shows:
- ✅ Connor system initialization with 13 agents
- ✅ Multi-agent processing pipeline working
- ✅ Integration between AutoGPT interface and Connor intelligence
- ✅ Successful task processing through all agent types

## Troubleshooting

### Import Errors
- Ensure PYTHONPATH includes both forge and autogpt directories
- Install all required dependencies
- Check Python version compatibility (3.10+)

### Configuration Issues
- Verify `.env` file has all required settings
- Check OpenAI API key is valid
- Ensure file permissions are correct

### Performance Issues
- Adjust `CONNOR_MAX_CONCURRENT_AGENTS` for your system
- Increase `CONNOR_PROCESSING_TIMEOUT` for complex tasks
- Monitor memory usage with large `CONNOR_MEMORY_SIZE`

## Future Enhancements

### Planned Features
- Web UI integration with Connor agent status
- Advanced learning agent family management
- Real-time performance monitoring dashboard
- Plugin system for specialized agent types

### Extension Points
- Custom agent types for domain-specific tasks
- Integration with external AI services
- Advanced memory and learning capabilities
- Multi-modal agent processing (text, images, audio)

---

This integration represents a significant advancement in AI assistant technology, combining AutoGPT's proven interface with Connor's sophisticated multi-agent intelligence to create a truly powerful and intelligent system.