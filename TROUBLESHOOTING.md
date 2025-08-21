This page is a list of issues you could encounter along with their fixes.

# Connor System Setup & Integration

## Installation Issues

**Problem**: `pip install -e .` fails with "No file/folder found for package connor"

**Solution**: This was fixed in the packaging update. Ensure you have the latest code and try:
```bash
pip install -e .
```

**Problem**: `ModuleNotFoundError: No module named 'forge'` or `ModuleNotFoundError: No module named 'litellm'`

**Solution**: Install the package with dependencies:
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Connor with dependencies
pip install -e .
```

## Command Usage

**✅ Correct invocation methods:**
```bash
# Main CLI with Connor integration
connor --help
connor agent start connor

# Connor-specific automation CLI  
connor-cli --help
connor-cli start

# Direct Python execution (fallback)
python cli.py --help
python connor_cli.py start
```

**❌ Avoid these (will not work):**
```bash
setup            # Use: connor setup OR connor-cli setup
agent connor     # Use: connor agent start connor
python -m connor # Use: connor directly
```

## Expected Non-Fatal Warnings

The following warnings are expected and **do not prevent Connor from working**:

- **Poetry warnings**: `poetry: not found` - Connor works with pip installation
- **Optional AI/ML dependencies**: Missing transformers, torch, etc. - Core functionality works without these
- **Pydantic deprecation warnings**: These are from dependencies and don't affect functionality

## Development Setup for New Contributors

**Complete setup sequence:**
```bash
# 1. Clone repository and create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install in editable mode
pip install -e .

# 3. Verify installation
connor --help
python -c "import forge; import connor; print('All imports successful')"

# 4. Run tests
python -m pytest tests/ -v
```

For more detailed troubleshooting, see the sections below.

# Forge
**Poetry configuration invalid**

The poetry configuration is invalid: 
- Additional properties are not allowed ('group' was unexpected)
<img width="487" alt="Screenshot 2023-09-22 at 5 42 59 PM" src="https://github.com/Significant-Gravitas/AutoGPT/assets/9652976/dd451e6b-8114-44de-9928-075f5f06d661">

**Pydantic Validation Error**

Remove your sqlite agent.db file. it's probably because some of your data is not complying with the new spec (we will create migrations soon to avoid this problem)


*Solution*

Update poetry

# Benchmark
TODO

# Frontend
TODO
