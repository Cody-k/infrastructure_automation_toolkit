"""Resource optimizer | Actionable optimization recommendations"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Optimization:
    """Optimization recommendation"""

    resource: str
    current_usage: float
    priority: str
    action: str
    impact: str
    potential_savings: float = 0.0


class ResourceOptimizer:
    """Generate intelligent optimization recommendations"""

    def analyze_memory_usage(self, memory_percent: float, available_gb: float) -> list[Optimization]:
        """Analyze memory and suggest optimizations"""
        optimizations = []

        if memory_percent > 90:
            optimizations.append(
                Optimization(
                    resource="memory",
                    current_usage=memory_percent,
                    priority="critical",
                    action="Memory critical - investigate high-memory processes or increase RAM",
                    impact="System instability, OOM kills likely",
                    potential_savings=0.0,
                )
            )
        elif memory_percent > 80:
            optimizations.append(
                Optimization(
                    resource="memory",
                    current_usage=memory_percent,
                    priority="high",
                    action=f"Memory at {memory_percent:.1f}% - monitor trends, identify memory leaks",
                    impact="Approaching threshold, plan capacity",
                    potential_savings=0.0,
                )
            )

        return optimizations

    def analyze_disk_usage(self, disk_percent: float, available_gb: float) -> list[Optimization]:
        """Analyze disk and suggest cleanup"""
        optimizations = []

        if disk_percent > 95:
            optimizations.append(
                Optimization(
                    resource="disk",
                    current_usage=disk_percent,
                    priority="critical",
                    action="Disk critical - clean logs, remove old containers/images immediately",
                    impact="Write failures imminent",
                    potential_savings=10.0,
                )
            )
        elif disk_percent > 85:
            optimizations.append(
                Optimization(
                    resource="disk",
                    current_usage=disk_percent,
                    priority="high",
                    action=f"Disk at {disk_percent:.1f}% - schedule cleanup (docker prune, log rotation)",
                    impact="Prevent write issues",
                    potential_savings=5.0,
                )
            )
        elif disk_percent > 75:
            optimizations.append(
                Optimization(
                    resource="disk",
                    current_usage=disk_percent,
                    priority="medium",
                    action="Disk trending high - review large files, old backups",
                    impact="Proactive capacity management",
                    potential_savings=3.0,
                )
            )

        return optimizations

    def analyze_docker_overhead(self, containers: list) -> list[Optimization]:
        """Identify Docker optimization opportunities"""
        optimizations = []

        stopped = [c for c in containers if c.status in ["exited", "stopped", "created"]]

        if len(stopped) > 10:
            optimizations.append(
                Optimization(
                    resource="containers",
                    current_usage=len(stopped),
                    priority="medium",
                    action=f"Remove {len(stopped)} stopped containers (docker container prune)",
                    impact="Free disk space, improve docker ps performance",
                    potential_savings=1.0,
                )
            )

        return optimizations

    def generate_all_recommendations(
        self, containers: list, system_metrics: dict
    ) -> list[Optimization]:
        """Generate comprehensive optimization recommendations"""
        all_opts = []

        all_opts.extend(self.analyze_docker_overhead(containers))

        if "memory_percent" in system_metrics:
            all_opts.extend(
                self.analyze_memory_usage(
                    system_metrics["memory_percent"],
                    system_metrics.get("memory_available_gb", 0),
                )
            )

        if "disk_percent" in system_metrics:
            all_opts.extend(
                self.analyze_disk_usage(
                    system_metrics["disk_percent"],
                    system_metrics.get("disk_available_gb", 0),
                )
            )

        return sorted(
            all_opts,
            key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.priority, 4),
        )
