"""Infrastructure Automation Toolkit | Comprehensive DevOps utilities"""

from .docker.manager import DockerManager, ContainerInfo, ContainerStats
from .monitoring.analyzer import ResourceAnalyzer, ResourceTrend, Prediction
from .monitoring.system_monitor import SystemMonitor, SystemMetrics
from .analysis.optimizer import ResourceOptimizer, Optimization
from .alerts.alert_manager import AlertManager, Alert

__version__ = "1.0.0"

__all__ = [
    "DockerManager",
    "ContainerInfo",
    "ContainerStats",
    "ResourceAnalyzer",
    "ResourceTrend",
    "Prediction",
    "SystemMonitor",
    "SystemMetrics",
    "ResourceOptimizer",
    "Optimization",
    "AlertManager",
    "Alert",
]
