#!/bin/bash

# Connor-AutoGPT Startup Script
# This script launches AutoGPT with Connor's multi-agent system integrated

echo "🚀 Starting Connor-AutoGPT Integrated System"
echo "================================================"

# Set up environment
cd "$(dirname "$0")"
export PYTHONPATH="${PWD}/../../forge:${PWD}:${PYTHONPATH}"

echo "📂 Working directory: $(pwd)"
echo "🐍 Python path includes Connor forge"

# Check if Connor system is available
echo "🔍 Checking Connor system availability..."
python -c "
try:
    from forge.connor.connor_system import ConnorSystem
    print('✅ Connor system is available')
    connor = ConnorSystem()
    print(f'✅ Connor system initialized with {len(connor.agents)} agents')
    print(f'📊 Agent types: {list(connor.agent_pools.keys())}')
except Exception as e:
    print(f'❌ Connor system error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "🎯 Launching AutoGPT with Connor multi-agent system..."
    echo ""
    
    # Launch AutoGPT with Connor integration
    python -m autogpt "$@"
else
    echo "❌ Failed to initialize Connor system"
    exit 1
fi