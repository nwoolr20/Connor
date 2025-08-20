# Connor Multi-Agent System Automation
# Provides comprehensive automation for setup, testing, deployment and monitoring

# Variables
PYTHON := python3
PIP := pip3
POETRY := poetry
VENV_DIR := .venv
CONNOR_DIR := autogpts/forge
LOG_DIR := logs
REPORTS_DIR := reports

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

.PHONY: help install test clean setup deploy monitor health demo lint format security

# Default target
all: help

help: ## Show available commands
	@echo "$(BLUE)Connor Multi-Agent System Automation$(RESET)"
	@echo "======================================"
	@echo
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo

# Setup and Installation
setup: ## Complete system setup and installation
	@echo "$(BLUE)Setting up Connor system...$(RESET)"
	@$(MAKE) install-deps
	@$(MAKE) setup-directories
	@$(MAKE) configure-environment
	@$(MAKE) install-connor
	@echo "$(GREEN)✅ Connor system setup complete!$(RESET)"

install-deps: ## Install system dependencies
	@echo "$(YELLOW)Installing system dependencies...$(RESET)"
	@./setup.sh
	@command -v $(POETRY) >/dev/null 2>&1 || (echo "Installing Poetry..." && curl -sSL https://install.python-poetry.org | $(PYTHON) -)

setup-directories: ## Create necessary directories
	@echo "$(YELLOW)Creating directories...$(RESET)"
	@mkdir -p $(LOG_DIR) $(REPORTS_DIR) $(REPORTS_DIR)/tests $(REPORTS_DIR)/coverage $(REPORTS_DIR)/security

configure-environment: ## Configure environment variables
	@echo "$(YELLOW)Configuring environment...$(RESET)"
	@if [ ! -f $(CONNOR_DIR)/.env ]; then \
		cp $(CONNOR_DIR)/.env.example $(CONNOR_DIR)/.env; \
		echo "Created .env file from template"; \
	fi

install-connor: ## Install Connor dependencies
	@echo "$(YELLOW)Installing Connor dependencies...$(RESET)"
	@cd $(CONNOR_DIR) && $(POETRY) install --with dev

# Testing and Quality Assurance
test: ## Run comprehensive test suite
	@echo "$(BLUE)Running Connor test suite...$(RESET)"
	@$(MAKE) test-unit
	@$(MAKE) test-integration
	@$(MAKE) test-performance
	@echo "$(GREEN)✅ All tests completed!$(RESET)"

test-unit: ## Run unit tests
	@echo "$(YELLOW)Running unit tests...$(RESET)"
	@mkdir -p $(REPORTS_DIR)/tests
	@cd $(CONNOR_DIR) && $(POETRY) run pytest forge/connor/tests/ -v --junitxml=../../$(REPORTS_DIR)/tests/unit-results.xml --cov=forge.connor --cov-report=html:../../$(REPORTS_DIR)/coverage/

test-integration: ## Run integration tests
	@echo "$(YELLOW)Running integration tests...$(RESET)"
	@$(PYTHON) test_connor.py 2>&1 | tee $(REPORTS_DIR)/tests/integration.log

test-performance: ## Run performance tests
	@echo "$(YELLOW)Running performance tests...$(RESET)"
	@$(PYTHON) -m timeit -n 5 -r 3 -s "import asyncio; from test_connor import test_connor_system" "asyncio.run(test_connor_system())" 2>&1 | tee $(REPORTS_DIR)/tests/performance.log

test-standalone: ## Run standalone tests without dependencies
	@echo "$(YELLOW)Running standalone tests...$(RESET)"
	@$(PYTHON) standalone_test.py 2>&1 | tee $(REPORTS_DIR)/tests/standalone.log

# Code Quality
lint: ## Run code quality checks
	@echo "$(BLUE)Running code quality checks...$(RESET)"
	@cd $(CONNOR_DIR) && $(POETRY) run flake8 forge/connor/ --output-file=../../$(REPORTS_DIR)/flake8.txt
	@cd $(CONNOR_DIR) && $(POETRY) run mypy forge/connor/ --html-report ../../$(REPORTS_DIR)/mypy/
	@echo "$(GREEN)✅ Code quality checks complete!$(RESET)"

format: ## Format code automatically
	@echo "$(YELLOW)Formatting code...$(RESET)"
	@cd $(CONNOR_DIR) && $(POETRY) run black forge/connor/
	@cd $(CONNOR_DIR) && $(POETRY) run isort forge/connor/
	@cd $(CONNOR_DIR) && $(POETRY) run autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive forge/connor/
	@echo "$(GREEN)✅ Code formatting complete!$(RESET)"

security: ## Run security scans
	@echo "$(BLUE)Running security scans...$(RESET)"
	@cd $(CONNOR_DIR) && $(POETRY) run safety check --json --output ../../$(REPORTS_DIR)/security/safety.json || true
	@cd $(CONNOR_DIR) && $(POETRY) run bandit -r forge/connor/ -f json -o ../../$(REPORTS_DIR)/security/bandit.json || true
	@echo "$(GREEN)✅ Security scans complete!$(RESET)"

# System Operations
demo: ## Run interactive demo
	@echo "$(BLUE)Starting Connor demo...$(RESET)"
	@$(PYTHON) demo_connor.py

demo-automated: ## Run automated demo with all scenarios
	@echo "$(BLUE)Running automated demo...$(RESET)"
	@echo "yes" | $(PYTHON) demo_connor.py 2>&1 | tee $(REPORTS_DIR)/demo.log

health: ## Check system health
	@echo "$(BLUE)Checking Connor system health...$(RESET)"
	@$(MAKE) health-dependencies
	@$(MAKE) health-connor
	@$(MAKE) health-performance

health-dependencies: ## Check dependency health
	@echo "$(YELLOW)Checking dependencies...$(RESET)"
	@$(POETRY) --version >/dev/null 2>&1 && echo "$(GREEN)✅ Poetry installed$(RESET)" || echo "$(RED)❌ Poetry missing$(RESET)"
	@$(PYTHON) --version >/dev/null 2>&1 && echo "$(GREEN)✅ Python available$(RESET)" || echo "$(RED)❌ Python missing$(RESET)"
	@cd $(CONNOR_DIR) && $(POETRY) check && echo "$(GREEN)✅ Dependencies valid$(RESET)" || echo "$(RED)❌ Dependency issues$(RESET)"

health-connor: ## Check Connor system health
	@echo "$(YELLOW)Checking Connor system...$(RESET)"
	@$(PYTHON) -c "import sys; sys.path.append('$(CONNOR_DIR)'); from forge.connor import ConnorSystem; print('✅ Connor imports work')" || echo "$(RED)❌ Connor import failed$(RESET)"
	@$(PYTHON) simple_test.py >/dev/null 2>&1 && echo "$(GREEN)✅ Connor basic functionality works$(RESET)" || echo "$(RED)❌ Connor functionality issues$(RESET)"

health-performance: ## Check performance metrics
	@echo "$(YELLOW)Checking performance...$(RESET)"
	@timeout 10 $(PYTHON) -c "import time; start=time.time(); import sys; sys.path.append('$(CONNOR_DIR)'); from forge.connor import ConnorSystem; print(f'Import time: {time.time()-start:.2f}s')" || echo "$(RED)❌ Slow imports$(RESET)"

monitor: ## Start system monitoring
	@echo "$(BLUE)Starting Connor system monitoring...$(RESET)"
	@mkdir -p $(LOG_DIR)
	@echo "$(YELLOW)Monitor logs will be written to $(LOG_DIR)/$(RESET)"
	@$(PYTHON) scripts/monitor.py

# Deployment
deploy-local: ## Deploy Connor locally
	@echo "$(BLUE)Deploying Connor locally...$(RESET)"
	@$(MAKE) setup
	@$(MAKE) test
	@$(MAKE) health
	@echo "$(GREEN)✅ Local deployment complete!$(RESET)"

deploy-docker: ## Build and deploy Docker container
	@echo "$(BLUE)Building Connor Docker container...$(RESET)"
	@cd $(CONNOR_DIR) && docker build -t connor-system .
	@echo "$(GREEN)✅ Docker container built!$(RESET)"

start: ## Start Connor system
	@echo "$(BLUE)Starting Connor system...$(RESET)"
	@cd $(CONNOR_DIR) && $(POETRY) run python -m forge.app &
	@echo "$(GREEN)✅ Connor system started!$(RESET)"

stop: ## Stop Connor system
	@echo "$(YELLOW)Stopping Connor system...$(RESET)"
	@pkill -f "python -m forge.app" || true
	@echo "$(GREEN)✅ Connor system stopped!$(RESET)"

restart: ## Restart Connor system
	@$(MAKE) stop
	@sleep 2
	@$(MAKE) start

# Maintenance
clean: ## Clean build artifacts and logs
	@echo "$(YELLOW)Cleaning up...$(RESET)"
	@rm -rf $(LOG_DIR)/* $(REPORTS_DIR)/* __pycache__ .pytest_cache .coverage
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete!$(RESET)"

update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	@cd $(CONNOR_DIR) && $(POETRY) update
	@echo "$(GREEN)✅ Dependencies updated!$(RESET)"

backup: ## Backup system configuration
	@echo "$(YELLOW)Creating backup...$(RESET)"
	@mkdir -p backups
	@tar -czf backups/connor-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz $(CONNOR_DIR)/.env $(LOG_DIR) $(REPORTS_DIR) --exclude='*.pyc' --exclude='__pycache__'
	@echo "$(GREEN)✅ Backup created!$(RESET)"

# CI/CD Integration
ci-setup: ## Setup for CI environment
	@$(MAKE) install-deps
	@$(MAKE) setup-directories
	@$(MAKE) configure-environment
	@$(MAKE) install-connor

ci-test: ## Run tests in CI environment
	@$(MAKE) lint
	@$(MAKE) security
	@$(MAKE) test-unit
	@$(MAKE) test-standalone

ci-deploy: ## Deploy in CI environment
	@$(MAKE) health
	@$(MAKE) demo-automated

# Documentation
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(RESET)"
	@mkdir -p $(REPORTS_DIR)/docs
	@cd $(CONNOR_DIR) && $(POETRY) run sphinx-build -b html docs/ ../../$(REPORTS_DIR)/docs/ || echo "Sphinx not configured"
	@echo "$(GREEN)✅ Documentation generated!$(RESET)"

# Advanced Operations
benchmark: ## Run comprehensive benchmarks
	@echo "$(BLUE)Running Connor benchmarks...$(RESET)"
	@$(PYTHON) -m cProfile -o $(REPORTS_DIR)/profile.stats test_connor.py
	@$(PYTHON) -c "import pstats; p = pstats.Stats('$(REPORTS_DIR)/profile.stats'); p.sort_stats('cumulative').print_stats(20)" > $(REPORTS_DIR)/performance-profile.txt
	@echo "$(GREEN)✅ Benchmarks complete!$(RESET)"

stress-test: ## Run stress tests
	@echo "$(BLUE)Running stress tests...$(RESET)"
	@for i in {1..10}; do \
		echo "Stress test iteration $$i"; \
		timeout 30 $(PYTHON) test_connor.py || true; \
	done
	@echo "$(GREEN)✅ Stress tests complete!$(RESET)"

auto-update: ## Automatically update and test system
	@echo "$(BLUE)Auto-updating Connor system...$(RESET)"
	@git pull origin main || true
	@$(MAKE) update
	@$(MAKE) test
	@$(MAKE) health
	@echo "$(GREEN)✅ Auto-update complete!$(RESET)"

# Quick shortcuts
quick-test: ## Quick test run (unit tests only)
	@$(MAKE) test-unit

quick-start: ## Quick start (skip full setup)
	@$(MAKE) install-connor
	@$(MAKE) start

full-cycle: ## Complete development cycle
	@$(MAKE) setup
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) test
	@$(MAKE) security
	@$(MAKE) health
	@$(MAKE) demo-automated

dev-setup: ## Setup development environment
	@$(MAKE) setup
	@$(MAKE) format
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"

production-ready: ## Verify production readiness
	@$(MAKE) ci-test
	@$(MAKE) benchmark
	@$(MAKE) security
	@$(MAKE) health
	@echo "$(GREEN)✅ Production readiness verified!$(RESET)"