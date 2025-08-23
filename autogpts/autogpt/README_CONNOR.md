# Connor-AutoGPT: Integrated Multi-Agent AI System

**The perfect fusion of AutoGPT's proven interface with Connor's sophisticated multi-agent intelligence.**

🤖 **Connor Multi-Agent System**: 13 specialized AI agents working in concert  
🚀 **AutoGPT Interface**: Familiar, reliable, and feature-rich user experience  
🎯 **Seamless Integration**: Best of both worlds in one powerful system  

---

## 🌟 What Makes This Special

This isn't just AutoGPT with plugins - it's a fundamental enhancement where Connor's multi-agent system **replaces** AutoGPT's single-agent decision making while preserving everything users love about AutoGPT's interface.

### Before: Single Agent Decision Making
```
User Input → AutoGPT Agent → Decision → Action
```

### After: Multi-Agent Intelligence
```
User Input → AutoGPT Interface → Connor Multi-Agent System → Optimized Decision → Action
                                 ↓
                    SRA → MBR → GAP → LA → UBA → AA
                    3     2     2     4    1     1
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install litellm chromadb sqlalchemy fastapi uvicorn python-multipart sentry-sdk
```

### 2. Configure Environment
```bash
cp .env.connor .env
# Edit .env and add your OpenAI API key
```

### 3. Launch Connor-AutoGPT
```bash
# Option 1: Integrated launcher (Recommended)
./run_connor_autogpt.sh --continuous

# Option 2: Demo mode (For testing)
python connor_autogpt_demo.py

# Option 3: Main entry point
python connor_autogpt.py --gpt4only --ai-name "Connor"
```

## 🎯 Key Benefits

### For Users
- **Zero Learning Curve**: Same AutoGPT commands and interface you know
- **Smarter Decisions**: 13 specialized agents analyze every request
- **Better Results**: Multi-agent consensus instead of single-agent guessing
- **Adaptive Learning**: System learns from your interactions and improves

### For Developers  
- **Proven Foundation**: Built on AutoGPT's tested infrastructure
- **Advanced AI**: Connor's sophisticated multi-agent reasoning
- **Easy Extension**: Add new agent types or modify behavior
- **Production Ready**: Scalable, reliable, and maintainable

## 🏗️ Architecture

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

## 📊 Connor Multi-Agent System

### Agent Types & Roles

| Agent Type | Count | Role | Function |
|------------|--------|------|----------|
| **SRA** - Simple Reflex Agent | 3 | First Response | Immediate categorization and basic processing |
| **MBR** - Model-Based Reflex Agent | 2 | Context Analysis | Memory-aware processing with environmental modeling |
| **GAP** - Goal-Based Agent-Planner | 2 | Strategic Planning | Goal decomposition and step-by-step planning |
| **LA** - Learning Agent | 4 | Adaptation | Pattern recognition, learning, and improvement |
| **UBA** - Utility-Based Agent | 1 | Optimization | Resource allocation and utility maximization |
| **AA** - Apprentice Agent | 1 | User Learning | Personalization and interaction learning |

### Processing Pipeline

```
1. SRA: "This is a web development task requiring research"
         ↓
2. MBR: "Based on previous similar tasks, focus on these frameworks"
         ↓
3. GAP: "Break into: research → plan → implement → test → deploy"
         ↓
4. LA:  "Similar patterns suggest starting with React for frontend"
         ↓
5. UBA: "Optimize for time vs. quality based on constraints"
         ↓
6. AA:  "User prefers detailed explanations, adjust response style"
```

## 📊 System Performance

```
🚀 Testing Connor Multi-Agent System
==================================================
✅ System initialized with 13 agents
📊 Agent distribution: 
   Simple Reflex Agent: 3
   Model-Based Reflex Agent: 2  
   Goal-Based Agent-Planner: 2
   Learning Agent: 4
   Utility-Based Agent: 1
   Apprentice Agent: 1
✅ Success Rate: 100.0%
✅ Multi-agent processing pipeline fully operational
```

## ⚙️ Configuration

### Environment Variables (.env)

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

# Performance Tuning
CONNOR_MAX_CONCURRENT_AGENTS=5
CONNOR_PROCESSING_TIMEOUT=30
CONNOR_MEMORY_SIZE=1000
CONNOR_LEARNING_ENABLED=true
```

### AutoGPT Commands (Enhanced)

All standard AutoGPT commands now use Connor's multi-agent intelligence:

```bash
# Continuous mode with multi-agent decision making
./run_connor_autogpt.sh --continuous

# GPT-4 mode optimized by Connor's utility-based agent  
./run_connor_autogpt.sh --gpt4only

# Custom AI settings with Connor's adaptive learning
./run_connor_autogpt.sh --ai-name "Connor-Assistant" --ai-role "Multi-Agent AI"

# Debug mode with agent insights
./run_connor_autogpt.sh --debug --log-level DEBUG
```

## 🧪 Testing & Verification

### Run the Integration Demo
```bash
cd autogpts/autogpt
python connor_autogpt_demo.py
```

Expected output:
- ✅ Connor system initialization with 13 agents
- ✅ Multi-agent processing pipeline working
- ✅ Integration between AutoGPT interface and Connor intelligence
- ✅ Successful task processing through all agent types

### Verify Integration
```bash
cd autogpts/autogpt
PYTHONPATH="../forge:." python -c "
from forge.connor.connor_system import ConnorSystem
from autogpt.agents.connor_agent import ConnorAgent
print('✅ Connor-AutoGPT integration verified')
"
```

## 🔧 Development

### Adding Custom Agents
```python
# In forge/connor/custom_agent.py
class CustomSpecializedAgent(BaseConnorAgent):
    async def process_request(self, request: ProcessingRequest) -> Dict[str, Any]:
        # Your specialized logic here
        return {"recommendation": "custom_action", "confidence": 0.9}

# Register in connor_system.py
custom_agent = CustomSpecializedAgent(config)
self.agents[custom_agent.agent_id] = custom_agent
```

### Customizing AutoGPT Integration
Modify `autogpt/agents/connor_agent.py` to change how Connor's responses map to AutoGPT commands.

### Performance Tuning
- Adjust `CONNOR_MAX_CONCURRENT_AGENTS` for your system capabilities
- Increase `CONNOR_PROCESSING_TIMEOUT` for complex tasks
- Optimize `CONNOR_MEMORY_SIZE` based on available RAM

## 🚨 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure paths are correct
export PYTHONPATH="/path/to/Connor/autogpts/forge:/path/to/Connor/autogpts/autogpt:$PYTHONPATH"
```

**Missing Dependencies**
```bash
pip install litellm chromadb sqlalchemy fastapi uvicorn python-multipart sentry-sdk
```

**Configuration Issues**
```bash
# Copy the template and configure
cp .env.connor .env
# Edit .env and add your OpenAI API key
```

### Performance Optimization

**For Low-Resource Systems:**
```env
CONNOR_MAX_CONCURRENT_AGENTS=2
CONNOR_MEMORY_SIZE=500
CONNOR_PROCESSING_TIMEOUT=15
```

**For High-Performance Systems:**
```env
CONNOR_MAX_CONCURRENT_AGENTS=10
CONNOR_MEMORY_SIZE=2000
CONNOR_PROCESSING_TIMEOUT=60
```

## 📚 Documentation

- **[Integration Guide](CONNOR_INTEGRATION.md)**: Detailed technical documentation
- **[AutoGPT Docs](https://docs.agpt.co/)**: Original AutoGPT documentation
- **[Connor System](../../README.md)**: Connor multi-agent system documentation

## 🎉 What's Next

This integration represents a significant advancement in AI assistant technology. Future enhancements include:

- **Web UI Integration**: Real-time Connor agent status in AutoGPT's web interface
- **Advanced Learning**: Improved learning agent families with generational knowledge transfer
- **Performance Monitoring**: Dashboard for multi-agent system performance
- **Plugin Ecosystem**: Connor-aware plugins for specialized tasks

---

**🤖 Connor-AutoGPT: Where proven interface meets advanced intelligence.**

*The future of AI assistants is here - and it's collaborative, intelligent, and ready for anything.*