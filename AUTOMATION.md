# Connor System Automation

This directory contains comprehensive automation tools for the Connor Multi-Agent System.

## 🚀 Quick Start

### One-Command Setup
```bash
# Complete system setup and verification
make setup

# Quick start (development)
make dev-setup

# Production deployment
make production-ready
```

### Using the Connor CLI
```bash
# Setup system
./connor_cli.py setup

# Run tests
./connor_cli.py test --type unit

# Check health
./connor_cli.py health

# Deploy system
./connor_cli.py deploy --env production

# Start monitoring
./connor_cli.py health --continuous
```

## 📁 Automation Components

### 1. Makefile - Build System Automation
The `Makefile` provides comprehensive automation for:
- **Setup & Installation**: `make setup`, `make install-deps`
- **Testing**: `make test`, `make test-unit`, `make test-integration`
- **Code Quality**: `make lint`, `make format`, `make security`
- **Health Monitoring**: `make health`, `make monitor`
- **Deployment**: `make deploy-local`, `make deploy-docker`
- **Maintenance**: `make clean`, `make update`, `make backup`

### 2. CI/CD Pipeline (.github/workflows/connor-ci-cd.yml)
Automated GitHub Actions workflow providing:
- **Continuous Integration**: Code quality, testing, security scans
- **Automated Deployment**: Staging and production deployments
- **Health Monitoring**: Scheduled health checks and alerting
- **Performance Testing**: Automated benchmarks and optimization
- **Multi-Environment Support**: Local, dev, staging, production

### 3. System Monitor (scripts/monitor.py)
Real-time system monitoring with:
- **Health Checks**: System, dependencies, Connor agents
- **Performance Metrics**: Processing time, memory usage, throughput
- **Alerting**: Configurable thresholds and notifications
- **Automated Reports**: JSON metrics and log analysis
- **Continuous Monitoring**: Scheduled health checks

### 4. Deployment Automation (scripts/deploy.py)
Comprehensive deployment automation:
- **Environment Setup**: Automated configuration management
- **Dependency Management**: Poetry integration and validation
- **Health Verification**: Post-deployment testing
- **Service Management**: Systemd service creation
- **Rollback Support**: Automatic failure recovery

### 5. Auto-Update System (scripts/auto_update.py)
Intelligent update management:
- **Version Control**: Git-based update detection
- **Dependency Updates**: Poetry package management
- **Safety Checks**: Security vulnerability scanning
- **Backup & Restore**: Automatic backup before updates
- **Verification Testing**: Post-update validation

### 6. Connor CLI (connor_cli.py)
Unified command-line interface:
- **System Management**: Start, stop, restart, status
- **Testing**: All test types with filtering options
- **Deployment**: Multi-environment deployment
- **Monitoring**: Health checks and continuous monitoring
- **Maintenance**: Updates, backups, cleanup

## 🔧 Configuration

### System Configuration (connor_config.json)
Centralized configuration for:
- **Agent Settings**: Instance counts, scaling thresholds
- **Performance Tuning**: Timeouts, resource limits
- **Monitoring**: Alert thresholds, retention policies  
- **Security**: Authentication, rate limiting
- **Automation**: Auto-scaling, maintenance schedules

### Environment Variables
Key automation settings:
```bash
CONNOR_ENV=production          # Environment name
CONNOR_LOG_LEVEL=INFO         # Logging level
CONNOR_MONITOR_INTERVAL=30    # Health check interval
CONNOR_MAX_AGENTS=50          # Agent scaling limit
CONNOR_AUTO_UPDATE=true       # Enable auto-updates
```

## 📊 Automation Features

### ✅ Complete Setup Automation
- **One-Command Setup**: `make setup` handles everything
- **Dependency Management**: Automatic Poetry installation
- **Environment Configuration**: Automated .env setup
- **Health Verification**: Post-setup validation

### 🧪 Comprehensive Testing
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end system testing
- **Performance Tests**: Benchmarking and profiling
- **Standalone Tests**: No-dependency validation
- **Automated Reports**: Coverage and performance metrics

### 🔍 Intelligent Monitoring
- **Real-time Health Checks**: System and agent monitoring
- **Performance Metrics**: Processing time and resource usage
- **Automated Alerting**: Configurable thresholds
- **Historical Analysis**: Trend analysis and reporting

### 🚀 Zero-Downtime Deployment
- **Environment Management**: Multi-stage deployments
- **Health Verification**: Pre and post-deployment checks
- **Rollback Automation**: Automatic failure recovery
- **Service Management**: Systemd integration

### 🔄 Continuous Updates
- **Automated Updates**: Git and dependency updates
- **Safety Verification**: Security scanning and testing
- **Backup Management**: Automatic backup and restore
- **Update Reports**: Detailed change tracking

### 📈 Performance Optimization
- **Auto-scaling**: Dynamic agent scaling
- **Resource Monitoring**: Memory and CPU tracking
- **Performance Tuning**: Automated optimization
- **Benchmark Tracking**: Performance trend analysis

## 🎯 Common Automation Workflows

### Development Workflow
```bash
# Setup development environment
make dev-setup

# Run full development cycle
make full-cycle

# Continuous testing and monitoring
make monitor &
make test
```

### Production Deployment
```bash
# Verify production readiness
make production-ready

# Deploy to production
./connor_cli.py deploy --env production

# Monitor deployment
./connor_cli.py health --continuous
```

### Maintenance Workflow
```bash
# Automated system update
./connor_cli.py update

# Health check and cleanup
./connor_cli.py health
./connor_cli.py cleanup

# Create backup
./connor_cli.py backup
```

### CI/CD Automation
The GitHub Actions workflow automatically:
1. **Code Quality**: Linting, formatting, security scans
2. **Testing**: Unit, integration, performance tests
3. **Health Monitoring**: System health verification
4. **Deployment**: Automated staging/production deploys
5. **Alerting**: Failure notifications and reporting

## 📋 Automation Commands Reference

### Setup Commands
```bash
make setup              # Complete system setup
make install-deps       # Install dependencies only
make configure-environment  # Setup environment files
```

### Testing Commands  
```bash
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-performance  # Performance tests only
make quick-test        # Fast unit test run
```

### Quality Commands
```bash
make lint              # Code quality checks
make format            # Auto-format code
make security          # Security scans
```

### Monitoring Commands
```bash
make health            # System health check
make monitor           # Start monitoring
make benchmark         # Run benchmarks
```

### Deployment Commands
```bash
make deploy-local      # Local deployment
make deploy-docker     # Docker deployment
make start             # Start system
make stop              # Stop system
make restart           # Restart system
```

### Maintenance Commands
```bash
make clean             # Clean artifacts
make update            # Update dependencies
make backup            # Create backup
make auto-update       # Automated update cycle
```

## 🔧 Customization

### Adding Custom Automation
1. **Add Makefile targets** for new automation tasks
2. **Extend monitor.py** for custom health checks
3. **Update connor_config.json** for new settings
4. **Modify CI/CD workflow** for custom pipelines

### Configuration Customization
- Edit `connor_config.json` for system settings
- Modify `.env` files for environment-specific config
- Update GitHub Actions workflow for custom CI/CD
- Customize monitoring thresholds and alerts

## 🚨 Troubleshooting

### Common Issues
- **Permission Errors**: Run `chmod +x scripts/*.py`
- **Missing Dependencies**: Run `make install-deps`
- **Configuration Issues**: Check `connor_config.json`
- **Health Check Failures**: Run `make health` for diagnostics

### Debug Mode
```bash
# Enable verbose logging
export CONNOR_LOG_LEVEL=DEBUG

# Run with detailed output
make health
./connor_cli.py health --continuous
```

### Recovery Procedures
```bash
# Restore from backup
./connor_cli.py update --backup-only
./scripts/deploy.py --rollback

# Reset to clean state
make clean
make setup
```

This automation system provides comprehensive, reliable, and scalable automation for the Connor Multi-Agent System, enabling efficient development, deployment, and maintenance workflows.