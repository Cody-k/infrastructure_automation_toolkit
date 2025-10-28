# Infrastructure Automation Toolkit

DevOps utilities for Docker/Podman management and system monitoring.

## Overview

Automation for infrastructure operations. Patterns extracted from managing 7-node homelab with 11 containers and 6+ weeks continuous uptime.

## Features

- **Container Management** - Docker/Podman health monitoring, auto-restart
- **Resource Monitoring** - CPU, memory, disk, load average tracking
- **Health Checks** - System diagnostics (services, disk, temperature)
- **Threshold Alerts** - Configurable warnings for resource limits

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Quick Start

```python
from src import ContainerManager, ResourceMonitor, SystemHealthCheck

# Monitor containers
manager = ContainerManager()
containers = manager.list_containers()
for container in containers:
    health = manager.health_check(container.name)
    print(f"{container.name}: {health['health']}")

# Check system resources
monitor = ResourceMonitor()
metrics = monitor.get_metrics()
warnings = monitor.check_thresholds(metrics)

# Run health diagnostics
checker = SystemHealthCheck()
status = checker.run_check()
print(f"System: {status.status}")
```

## Examples

```bash
python examples/infrastructure_monitoring.py
```

## Structure

```
src/
├── docker/
│   └── container_manager.py      # Container operations
├── monitoring/
│   └── resource_monitor.py       # System metrics
└── system/
    └── health_check.py            # Health diagnostics

tests/                             # Test suite
examples/                          # Workflows
```

## Background

Patterns from infrastructure managing:
- 7-node network (workstation, server, NAS, RPi)
- 11 Docker containers with Portainer orchestration
- 6+ weeks continuous uptime
- Automated monitoring and recovery

## Technologies

Python 3.11+ · subprocess · pytest · Ruff

*No external dependencies* - uses system tools (docker, df, free, sensors)

## License

MIT

---

**Author:** Cody Kickertz
**Contact:** [LinkedIn](https://linkedin.com/in/Cody-Kickertz/)
