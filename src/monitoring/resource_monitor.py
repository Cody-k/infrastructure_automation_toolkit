"""Resource monitoring | System metrics collection and analysis"""

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Optional


@dataclass
class SystemMetrics:
    """System resource metrics"""

    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_percent: float
    disk_available_gb: float
    load_average_1min: float


class ResourceMonitor:
    """Monitor system resource usage"""

    def get_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics"""
        try:
            cpu = self._get_cpu_percent()
            memory_pct, memory_avail = self._get_memory()
            disk_pct, disk_avail = self._get_disk()
            load = self._get_load_average()

            return SystemMetrics(
                cpu_percent=cpu,
                memory_percent=memory_pct,
                memory_available_gb=memory_avail,
                disk_percent=disk_pct,
                disk_available_gb=disk_avail,
                load_average_1min=load,
            )
        except Exception:
            return None

    def check_thresholds(self, metrics: SystemMetrics) -> list[str]:
        """Check if metrics exceed safe thresholds"""
        warnings = []

        if metrics.cpu_percent > 80:
            warnings.append(f"High CPU: {metrics.cpu_percent:.1f}%")

        if metrics.memory_percent > 85:
            warnings.append(f"High memory: {metrics.memory_percent:.1f}%")

        if metrics.disk_percent > 90:
            warnings.append(f"Low disk space: {metrics.disk_percent:.1f}% used")

        if metrics.load_average_1min > 8:
            warnings.append(f"High load: {metrics.load_average_1min:.2f}")

        return warnings

    def _get_cpu_percent(self) -> float:
        """Get CPU usage percentage"""
        try:
            result = subprocess.run(
                ["top", "-bn1"],
                capture_output=True,
                text=True,
                check=True,
                timeout=2,
            )
            for line in result.stdout.split("\n"):
                if "Cpu(s)" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "id" in part and i > 0:
                            idle = float(parts[i - 1])
                            return 100.0 - idle
        except Exception:
            pass
        return 0.0

    def _get_memory(self) -> tuple[float, float]:
        """Get memory usage percentage and available GB"""
        try:
            result = subprocess.run(
                ["free", "-g"], capture_output=True, text=True, check=True
            )
            lines = result.stdout.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 7:
                    total = float(parts[1])
                    available = float(parts[6])
                    used_percent = ((total - available) / total) * 100
                    return used_percent, available
        except Exception:
            pass
        return 0.0, 0.0

    def _get_disk(self) -> tuple[float, float]:
        """Get disk usage percentage and available GB"""
        try:
            result = subprocess.run(
                ["df", "-BG", "/"], capture_output=True, text=True, check=True
            )
            lines = result.stdout.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    percent_str = parts[4].rstrip("%")
                    available_str = parts[3].rstrip("G")
                    return float(percent_str), float(available_str)
        except Exception:
            pass
        return 0.0, 0.0

    def _get_load_average(self) -> float:
        """Get 1-minute load average"""
        try:
            with open("/proc/loadavg") as f:
                return float(f.read().split()[0])
        except Exception:
            return 0.0
