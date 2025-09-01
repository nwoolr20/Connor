# Connor Multi-Agent System - Usage Example

## Installation and Setup

```bash
# 1. Install the system (single command)
python install.py

# 2. Launch the system (single entry point)
python launch_connor.py --help
```

## Quick Start Commands

```bash
# Run comprehensive system audit
python launch_connor.py audit

# Check system health
python launch_connor.py status

# Run system tests
python launch_connor.py test

# Start the Connor system
python launch_connor.py start

# Run interactive demo
python launch_connor.py demo

# Start chat interface
python launch_connor.py chat
```

## System Status

After successful installation, you should see:

- ✅ All 6 Connor agent types (SRA, MBR, GAP, LA, UBA, AA) loading successfully
- ✅ System health check showing 71%+ health score
- ✅ 13 agents initialized across multiple families
- ✅ All core dependencies (litellm, chromadb, fastapi, etc.) available

## Entry Points Simplified

The system now has only **two** main entry points:

1. **`python install.py`** - Single installation script for the entire system
2. **`python launch_connor.py`** - Single unified launcher for all operations

This eliminates confusion from multiple CLI scripts and provides a clean, simple interface.