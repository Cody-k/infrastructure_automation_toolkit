"""System health check | Comprehensive diagnostics"""

from dataclasses import dataclass
from typing import Optional
import subprocess
from pathlib import Path


@dataclass
class HealthStatus:
    """System health status"""

    status: str
    failed_services: list[str]
    disk_warnings: list[str]
    memory_warnings: list[str]
    temperature_warnings: list[str]


class SystemHealthCheck:
    """Perform comprehensive system health diagnostics"""

    def run_check(self) -> HealthStatus:
        """Execute full health check"""
        failed_services = self._check_failed_services()
        disk_warnings = self._check_disk_space()
        memory_warnings = self._check_memory()
        temp_warnings = self._check_temperatures()

        status = "healthy"
        if failed_services or disk_warnings or any(
            "critical" in w.lower() for w in memory_warnings + temp_warnings
        ):
            status = "degraded"

        return HealthStatus(
            status=status,
            failed_services=failed_services,
            disk_warnings=disk_warnings,
            memory_warnings=memory_warnings,
            temperature_warnings=temp_warnings,
        )

    def _check_failed_services(self) -> list[str]:
        """Check for failed systemd services"""
        try:
            result = subprocess.run(
                ["systemctl", "--failed", "--no-pager", "--no-legend"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            failed = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    service_name = line.split()[0]
                    failed.append(service_name)
            return failed
        except Exception:
            return []

    def _check_disk_space(self) -> list[str]:
        """Check disk space on all mount points"""
        warnings = []
        try:
            result = subprocess.run(
                ["df", "-h"], capture_output=True, text=True, check=True
            )
            for line in result.stdout.split("\n")[1:]:
                if line:
                    parts = line.split()
                    if len(parts) >= 5:
                        percent_str = parts[4].rstrip("%")
                        try:
                            usage = int(percent_str)
                            if usage > 90:
                                warnings.append(f"{parts[5]}: {usage}% used")
                        except ValueError:
                            pass
        except Exception:
            pass
        return warnings

    def _check_memory(self) -> list[str]:
        """Check memory usage"""
        warnings = []
        try:
            result = subprocess.run(
                ["free", "-h"], capture_output=True, text=True, check=True
            )
            lines = result.stdout.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 3:
                    try:
                        total_str = parts[1].rstrip("GgiMmKk")
                        used_str = parts[2].rstrip("GgiMmKk")
                        total = float(total_str)
                        used = float(used_str)
                        percent = (used / total) * 100
                        if percent > 90:
                            warnings.append(f"Memory {percent:.1f}% used")
                    except ValueError:
                        pass
        except Exception:
            pass
        return warnings

    def _check_temperatures(self) -> list[str]:
        """Check CPU temperatures if sensors available"""
        warnings = []
        try:
            result = subprocess.run(
                ["sensors"], capture_output=True, text=True, timeout=3
            )
            for line in result.stdout.split("\n"):
                if "Core" in line and "°C" in line:
                    try:
                        temp_str = line.split("+")[1].split("°")[0]
                        temp = float(temp_str)
                        if temp > 90:
                            warnings.append(f"CPU temp: {temp}°C")
                    except (IndexError, ValueError):
                        pass
        except Exception:
            pass
        return warnings
