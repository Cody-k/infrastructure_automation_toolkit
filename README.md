# Infrastructure Automation Toolkit

Comprehensive DevOps automation for container orchestration and intelligent resource management.

## Features

**Container Management**
- Health monitoring with status tracking
- Resource hog identification (CPU/memory thresholds)
- Detailed statistics (CPU delta, memory, network I/O, block I/O)
- Container lifecycle operations (start, stop, restart, pause)
- Log retrieval and inspection
- Cleanup automation (stopped containers, dangling images)

**Resource Analysis**
- 24-hour trend tracking with linear regression
- Volatility calculations for stability assessment
- Direction detection (increasing/decreasing/stable)
- Predictive forecasting (time-to-threshold with confidence scoring)
- 7-day and 30-day resource projections

**System Monitoring**
- Real-time metrics collection (psutil)
- Per-core CPU usage
- Detailed memory statistics (active, cached, buffers)
- Network interface tracking
- Top processes by CPU and memory
- Disk partition analysis

**Alert System**
- Severity-based alerts (info, low, medium, high, critical)
- Alert persistence and deduplication
- Acknowledgment tracking
- Automatic cleanup of old alerts

**Smart Recommendations**
- Priority-based suggestions (critical → low)
- Actionable optimization steps
- Impact assessments
- Container overhead analysis

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Usage

```python
from src import (
    SystemMonitor,
    ResourceAnalyzer,
    DockerManager,
    AlertManager,
    ResourceOptimizer,
)

# Collect current metrics
monitor = SystemMonitor()
metrics = monitor.collect_metrics()
print(f"CPU: {metrics.cpu_percent:.1f}%")

# Analyze trends (requires historical data)
analyzer = ResourceAnalyzer()
analyzer.record_metrics(
    cpu=metrics.cpu_percent,
    memory=metrics.memory_percent,
    disk=metrics.disk_percent,
    load=metrics.load_avg_1m,
)
trends = analyzer.analyze_trends(hours=24)

# Predictive forecasting
predictions = analyzer.predict_resource_needs()
for resource, pred in predictions.items():
    if pred.time_to_90_percent_hours:
        print(f"{resource}: {pred.time_to_90_percent_hours/24:.1f} days to 90%")

# Container analysis
docker = DockerManager()
containers = docker.list_all()
hogs = docker.identify_resource_hogs()

# Alert management
alerts = AlertManager()
warnings = monitor.check_thresholds(metrics)
for warning in warnings:
    alert = alerts.create_alert(
        alert_type=warning["metric"],
        severity=warning["severity"],
        message=warning["message"],
        value=warning["value"],
        threshold=warning["threshold"],
    )

# Optimization recommendations
optimizer = ResourceOptimizer()
recommendations = optimizer.generate_all_recommendations(containers, {...})
```

## Examples

```bash
python examples/complete_workflow.py
python examples/comprehensive_monitoring.py
```

## Architecture

```
src/
├── docker/
│   └── manager.py          # Container orchestration (270 LOC)
├── monitoring/
│   ├── system_monitor.py   # Metrics collection with psutil (180 LOC)
│   └── analyzer.py         # Trend analysis, predictions (240 LOC)
├── analysis/
│   └── optimizer.py        # Smart recommendations (130 LOC)
└── alerts/
    └── alert_manager.py    # Alert system (140 LOC)

tests/                      # 31 comprehensive tests
examples/                   # Complete workflows
```

## Testing

```bash
pytest -v  # 31 tests, all passing
```

## Capabilities

**Trend Analysis:**
- Linear regression for trend lines
- Volatility calculations (coefficient of variation)
- Statistical analysis (mean, min, max, stdev)
- Direction classification

**Predictive Forecasting:**
- Time-to-threshold calculations
- 7-day and 30-day projections
- Confidence assessment (high/medium/low based on volatility and data points)
- Trend stability detection

**Container Intelligence:**
- Detailed stats parsing (CPU delta calculation, network aggregation, block I/O)
- Health check monitoring
- Port and network inspection
- Resource hog detection

**Alert System:**
- Severity levels (info → critical)
- Persistence across restarts
- Deduplication (no repeat alerts)
- Acknowledgment workflow
- Automatic old alert cleanup

## Background

Patterns from homelab infrastructure managing:
- 7-node network (workstation, server, NAS, RPi)
- 11 Docker containers with Portainer
- 6+ weeks continuous uptime
- Automated monitoring and recovery

**Stats:** 1,199 LOC · 31 tests · Python 3.11+

## Technologies

Python 3.11+ · psutil · dataclasses · pytest · Ruff

*Optional:* docker (for container management)

## License

MIT

---

**Author:** Cody Kickertz
**Contact:** [LinkedIn](https://linkedin.com/in/Cody-Kickertz/)
