"""Infrastructure Automation Toolkit | DevOps utilities for container and system management"""

from .docker.manager import DockerManager, ContainerInfo, ContainerStats
from .monitoring.resource_analyzer import ResourceAnalyzer, ResourceTrend, Prediction
from .analysis.optimizer import ResourceOptimizer, Optimization

__version__ = "1.0.0"

__all__ = [
    "DockerManager",
    "ContainerInfo",
    "ContainerStats",
    "ResourceAnalyzer",
    "ResourceTrend",
    "Prediction",
    "ResourceOptimizer",
    "Optimization",
]
