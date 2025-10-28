"""Resource optimizer | Generate actionable optimization recommendations"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Optimization:
    """Resource optimization recommendation"""

    resource: str
    current_usage: float
    potential_savings: float
    action: str
    priority: str
    impact: str


class ResourceOptimizer:
    """Generate intelligent resource optimization recommendations"""

    def analyze_docker_overhead(self, containers: list, system_metrics: dict) -> list[Optimization]:
        """Identify Docker container resource optimization opportunities"""
        optimizations = []

        stopped_containers = [c for c in containers if c.status in ["exited", "stopped"]]
        if len(stopped_containers) > 5:
            optimizations.append(
                Optimization(
                    resource="containers",
                    current_usage=len(stopped_containers),
                    potential_savings=0.0,
                    action=f"Remove {len(stopped_containers)} stopped containers",
                    priority="low",
                    impact="Cleanup disk space, improve docker ps performance",
                )
            )

        return optimizations

    def analyze_memory_usage(self, memory_percent: float, available_gb: float) -> list[Optimization]:
        """Analyze memory usage and suggest optimizations"""
        optimizations = []

        if memory_percent > 85:
            optimizations.append(
                Optimization(
                    resource="memory",
                    current_usage=memory_percent,
                    potential_savings=0.0,
                    action="Investigate high memory processes, consider increasing RAM or reducing services",
                    priority="high",
                    impact="Prevent OOM kills, improve system stability",
                )
            )
        elif memory_percent > 70:
            optimizations.append(
                Optimization(
                    resource="memory",
                    current_usage=memory_percent,
                    potential_savings=0.0,
                    action="Monitor memory trends, identify memory leaks",
                    priority="medium",
                    impact="Proactive capacity planning",
                )
            )

        return optimizations

    def analyze_disk_usage(self, disk_percent: float, available_gb: float) -> list[Optimization]:
        """Analyze disk usage and suggest cleanup"""
        optimizations = []

        if disk_percent > 90:
            optimizations.append(
                Optimization(
                    resource="disk",
                    current_usage=disk_percent,
                    potential_savings=10.0,
                    action="Clean logs, remove old container images, clear package cache",
                    priority="high",
                    impact="Free critical disk space, prevent write failures",
                )
            )
        elif disk_percent > 75:
            optimizations.append(
                Optimization(
                    resource="disk",
                    current_usage=disk_percent,
                    potential_savings=5.0,
                    action="Schedule cleanup: docker system prune, log rotation",
                    priority="medium",
                    impact="Maintain adequate free space",
                )
            )

        return optimizations

    def generate_all_recommendations(
        self, containers: list, system_metrics: dict
    ) -> list[Optimization]:
        """Generate comprehensive optimization recommendations"""
        all_optimizations = []

        all_optimizations.extend(self.analyze_docker_overhead(containers, system_metrics))

        if "memory_percent" in system_metrics:
            all_optimizations.extend(
                self.analyze_memory_usage(
                    system_metrics["memory_percent"],
                    system_metrics.get("memory_available_gb", 0),
                )
            )

        if "disk_percent" in system_metrics:
            all_optimizations.extend(
                self.analyze_disk_usage(
                    system_metrics["disk_percent"], system_metrics.get("disk_available_gb", 0)
                )
            )

        return sorted(all_optimizations, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x.priority])
