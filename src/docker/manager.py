"""Docker manager | Container orchestration with async operations and detailed stats"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import subprocess
import json


@dataclass
class ContainerStats:
    """Container resource statistics"""

    cpu_percent: float
    memory_mb: float
    memory_limit_mb: float
    memory_percent: float
    network_rx_mb: float
    network_tx_mb: float
    block_read_mb: float
    block_write_mb: float


@dataclass
class ContainerInfo:
    """Container detailed information"""

    id: str
    name: str
    status: str
    image: str
    created: str
    health: str
    ports: list[str]
    networks: list[str]


class DockerManager:
    """Docker/Podman container management with health monitoring"""

    def __init__(self, runtime: str = "docker"):
        self.runtime = runtime
        self.available = self._check_runtime()

    def list_all(self, include_stopped: bool = True) -> list[ContainerInfo]:
        """List containers with detailed information"""
        if not self.available:
            return []

        cmd = [self.runtime, "ps", "--format", "json"]
        if include_stopped:
            cmd.append("-a")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            containers = []

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                data = json.loads(line)
                containers.append(
                    ContainerInfo(
                        id=data.get("ID", "")[:12],
                        name=data.get("Names", ""),
                        status=data.get("State", ""),
                        image=data.get("Image", ""),
                        created=data.get("CreatedAt", ""),
                        health=self._get_health_status(data.get("Names", "")),
                        ports=self._parse_ports(data.get("Ports", "")),
                        networks=data.get("Networks", "").split(",") if data.get("Networks") else [],
                    )
                )

            return containers
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []

    def get_stats(self, container_name: str) -> Optional[ContainerStats]:
        """Get detailed resource statistics for container"""
        if not self.available:
            return None

        cmd = [self.runtime, "stats", container_name, "--no-stream", "--format", "json"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
            data = json.loads(result.stdout)

            return ContainerStats(
                cpu_percent=self._parse_percent(data.get("CPUPerc", "0%")),
                memory_mb=self._parse_memory(data.get("MemUsage", "0B").split("/")[0]),
                memory_limit_mb=self._parse_memory(data.get("MemUsage", "0B / 0B").split("/")[1])
                if "/" in data.get("MemUsage", "")
                else 0,
                memory_percent=self._parse_percent(data.get("MemPerc", "0%")),
                network_rx_mb=self._parse_memory(data.get("NetIO", "0B / 0B").split("/")[0])
                if "/" in data.get("NetIO", "")
                else 0,
                network_tx_mb=self._parse_memory(data.get("NetIO", "0B / 0B").split("/")[1])
                if "/" in data.get("NetIO", "")
                else 0,
                block_read_mb=self._parse_memory(
                    data.get("BlockIO", "0B / 0B").split("/")[0]
                )
                if "/" in data.get("BlockIO", "")
                else 0,
                block_write_mb=self._parse_memory(
                    data.get("BlockIO", "0B / 0B").split("/")[1]
                )
                if "/" in data.get("BlockIO", "")
                else 0,
            )
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired):
            return None

    def identify_resource_hogs(self, threshold_cpu: float = 80.0, threshold_mem: float = 80.0) -> list[dict]:
        """Identify containers consuming excessive resources"""
        containers = self.list_all(include_stopped=False)
        hogs = []

        for container in containers:
            if container.status != "running":
                continue

            stats = self.get_stats(container.name)
            if not stats:
                continue

            if stats.cpu_percent > threshold_cpu or stats.memory_percent > threshold_mem:
                hogs.append({
                    "name": container.name,
                    "cpu_percent": stats.cpu_percent,
                    "memory_percent": stats.memory_percent,
                    "memory_mb": stats.memory_mb,
                    "reason": "High CPU" if stats.cpu_percent > threshold_cpu else "High memory",
                })

        return hogs

    def _get_health_status(self, container_name: str) -> str:
        """Get container health check status"""
        cmd = [self.runtime, "inspect", container_name, "--format", "{{.State.Health.Status}}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=2)
            status = result.stdout.strip()
            return status if status else "no_healthcheck"
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return "unknown"

    def _parse_ports(self, ports_str: str) -> list[str]:
        """Parse port mappings from string"""
        if not ports_str:
            return []
        return [p.strip() for p in ports_str.split(",") if p.strip()]

    def _parse_percent(self, percent_str: str) -> float:
        """Parse percentage string to float"""
        try:
            return float(percent_str.rstrip("%"))
        except ValueError:
            return 0.0

    def _parse_memory(self, mem_str: str) -> float:
        """Parse memory string to MB"""
        try:
            mem_str = mem_str.strip()
            if "GB" in mem_str or "GiB" in mem_str:
                return float(mem_str.replace("GiB", "").replace("GB", "")) * 1024
            elif "MB" in mem_str or "MiB" in mem_str:
                return float(mem_str.replace("MiB", "").replace("MB", ""))
            elif "KB" in mem_str or "KiB" in mem_str:
                return float(mem_str.replace("KiB", "").replace("KB", "")) / 1024
            else:
                return 0.0
        except ValueError:
            return 0.0

    def _check_runtime(self) -> bool:
        """Verify Docker/Podman is available"""
        try:
            subprocess.run([self.runtime, "ps"], capture_output=True, check=True, timeout=3)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
