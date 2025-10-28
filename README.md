# Infrastructure Automation Toolkit

DevOps utilities for container orchestration and intelligent resource management.

## Features

- **Container Management** - Health monitoring, resource hogs identification, automated operations
- **Trend Analysis** - 24-hour resource tracking with statistical analysis
- **Predictive Forecasting** - When will resources reach critical thresholds
- **Smart Recommendations** - Actionable optimization suggestions
- **Resource Metrics** - CPU, memory, disk, network, load average

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Quick Start

```python
from src import DockerManager, ResourceAnalyzer, ResourceOptimizer

# Container analysis
docker = DockerManager()
containers = docker.list_all()
hogs = docker.identify_resource_hogs(threshold_cpu=80.0)

# Trend analysis
analyzer = ResourceAnalyzer()
trends = analyzer.analyze_trends(hours=24)
print(f"CPU: {trends['cpu'].current:.1f}% ({trends['cpu'].trend_direction})")

# Predictive forecasting
predictions = analyzer.predict_resource_needs()
for resource, pred in predictions.items():
    print(f"{resource}: {pred.time_to_threshold/24:.1f} days to threshold")

# Optimization recommendations
optimizer = ResourceOptimizer()
recommendations = optimizer.generate_all_recommendations(containers, metrics)
for rec in recommendations:
    print(f"[{rec.priority}] {rec.action}")
```

## Examples

```bash
python examples/comprehensive_monitoring.py
```

## Structure

```
src/
├── docker/
│   └── manager.py              # Container orchestration
├── monitoring/
│   └── resource_analyzer.py    # Trend analysis, predictions
└── analysis/
    └── optimizer.py            # Smart recommendations

tests/                          # Comprehensive test suite
examples/                       # Complete workflows
```

## Capabilities

**Trend Analysis:**
- Historical resource tracking
- Linear regression for trends
- Volatility calculations
- Direction detection (increasing/decreasing/stable)

**Predictive Forecasting:**
- Time-to-threshold calculations
- Confidence scoring
- 7-day resource projections

**Smart Recommendations:**
- Priority-based suggestions (high/medium/low)
- Actionable optimization steps
- Impact assessments

**Container Intelligence:**
- Resource hog identification
- Health status monitoring
- Detailed statistics (CPU, memory, network, I/O)

## Background

Patterns from infrastructure managing 7-node homelab:
- 11 Docker containers with Portainer orchestration
- 6+ weeks continuous uptime
- Automated monitoring and recovery

## Technologies

Python 3.11+ · dataclasses · pytest · Ruff

*Zero external dependencies* - uses system tools (docker, df, free, top)

## License

MIT

---

**Author:** Cody Kickertz
**Contact:** [LinkedIn](https://linkedin.com/in/Cody-Kickertz/)
