"""Docker manager | Complete container orchestration with async operations"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
import json

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


@dataclass
class ContainerStats:
    """Container resource statistics"""

    cpu_percent: float
    memory_usage_bytes: int
    memory_limit_bytes: int
    memory_percent: float
    network_rx_bytes: int
    network_tx_bytes: int
    block_read_bytes: int
    block_write_bytes: int
    timestamp: str

    @property
    def memory_mb(self) -> float:
        return self.memory_usage_bytes / (1024 * 1024)

    @property
    def network_rx_mb(self) -> float:
        return self.network_rx_bytes / (1024 * 1024)

    @property
    def network_tx_mb(self) -> float:
        return self.network_tx_bytes / (1024 * 1024)


@dataclass
class ContainerInfo:
    """Container detailed information"""

    id: str
    name: str
    status: str
    image: str
    created: str
    started_at: Optional[str] = None
    ports: list[dict] = field(default_factory=list)
    labels: dict = field(default_factory=dict)
    health: Optional[dict] = None
    stats: Optional[ContainerStats] = None


class DockerManager:
    """Docker container management with health monitoring and lifecycle operations"""

    def __init__(self):
        if not DOCKER_AVAILABLE:
            self.client = None
            self.available = False
            return

        try:
            self.client = docker.from_env()
            self.available = True
            self.client.ping()
        except Exception:
            self.client = None
            self.available = False

    def list_all(self, include_stopped: bool = True) -> list[ContainerInfo]:
        """List all containers with detailed information and stats"""
        if not self.available:
            return []

        try:
            containers = self.client.containers.list(all=include_stopped)
            result = []

            for container in containers:
                stats = None
                if container.status == "running":
                    try:
                        stats_data = container.stats(stream=False)
                        stats = self._parse_stats(stats_data)
                    except Exception:
                        pass

                health = self._parse_health(container)

                result.append(
                    ContainerInfo(
                        id=container.short_id,
                        name=container.name,
                        status=container.status,
                        image=container.image.tags[0] if container.image.tags else container.image.short_id,
                        created=container.attrs["Created"],
                        started_at=container.attrs["State"].get("StartedAt"),
                        ports=self._parse_ports(container.ports),
                        labels=container.labels,
                        health=health,
                        stats=stats,
                    )
                )

            return result
        except Exception:
            return []

    def get_detailed_stats(self, container_name: str) -> Optional[ContainerStats]:
        """Get detailed resource statistics for specific container"""
        if not self.available:
            return None

        try:
            container = self.client.containers.get(container_name)
            if container.status != "running":
                return None

            stats_data = container.stats(stream=False)
            return self._parse_stats(stats_data)
        except Exception:
            return None

    def identify_resource_hogs(
        self, cpu_threshold: float = 80.0, memory_threshold: float = 80.0
    ) -> list[dict]:
        """Identify containers consuming excessive resources"""
        containers = self.list_all(include_stopped=False)
        hogs = []

        for container in containers:
            if not container.stats:
                continue

            is_cpu_hog = container.stats.cpu_percent > cpu_threshold
            is_mem_hog = container.stats.memory_percent > memory_threshold

            if is_cpu_hog or is_mem_hog:
                hogs.append({
                    "name": container.name,
                    "cpu_percent": container.stats.cpu_percent,
                    "memory_percent": container.stats.memory_percent,
                    "memory_mb": container.stats.memory_mb,
                    "issues": [
                        "High CPU" if is_cpu_hog else None,
                        "High memory" if is_mem_hog else None,
                    ],
                })

        return hogs

    def container_action(self, container_name: str, action: str) -> dict:
        """Execute action on container (start, stop, restart, pause, unpause)"""
        if not self.available:
            raise RuntimeError("Docker not available")

        container = self.client.containers.get(container_name)

        actions = {
            "start": container.start,
            "stop": lambda: container.stop(timeout=10),
            "restart": lambda: container.restart(timeout=10),
            "pause": container.pause,
            "unpause": container.unpause,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        actions[action]()
        container.reload()

        return {
            "container": container_name,
            "action": action,
            "new_status": container.status,
            "timestamp": datetime.now().isoformat(),
        }

    def get_logs(self, container_name: str, lines: int = 100) -> list[str]:
        """Retrieve container logs"""
        if not self.available:
            return []

        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=lines, timestamps=True).decode("utf-8", errors="ignore")
            return logs.split("\n") if logs else []
        except Exception:
            return []

    def cleanup_stopped(self) -> dict:
        """Remove stopped containers and dangling images"""
        if not self.available:
            return {"error": "Docker not available"}

        removed_containers = 0
        removed_images = 0
        space_reclaimed = 0
        errors = []

        try:
            stopped = self.client.containers.list(filters={"status": "exited"})
            for container in stopped:
                try:
                    container.remove()
                    removed_containers += 1
                except Exception as e:
                    errors.append(f"Container {container.name}: {e}")
        except Exception as e:
            errors.append(f"List stopped: {e}")

        try:
            dangling = self.client.images.list(filters={"dangling": True})
            for image in dangling:
                try:
                    size = image.attrs.get("Size", 0)
                    self.client.images.remove(image.id)
                    removed_images += 1
                    space_reclaimed += size
                except Exception as e:
                    errors.append(f"Image {image.short_id}: {e}")
        except Exception as e:
            errors.append(f"List images: {e}")

        return {
            "containers_removed": removed_containers,
            "images_removed": removed_images,
            "space_reclaimed_mb": round(space_reclaimed / (1024 * 1024), 2),
            "errors": errors,
            "timestamp": datetime.now().isoformat(),
        }

    def get_system_info(self) -> dict:
        """Get Docker system information"""
        if not self.available:
            return {}

        try:
            info = self.client.info()
            version = self.client.version()

            return {
                "containers_running": info.get("ContainersRunning", 0),
                "containers_paused": info.get("ContainersPaused", 0),
                "containers_stopped": info.get("ContainersStopped", 0),
                "images": info.get("Images", 0),
                "server_version": info.get("ServerVersion"),
                "storage_driver": info.get("Driver"),
                "kernel_version": info.get("KernelVersion"),
                "os": info.get("OperatingSystem"),
                "architecture": version.get("Arch"),
                "api_version": version.get("ApiVersion"),
            }
        except Exception:
            return {}

    def _parse_stats(self, stats: dict) -> Optional[ContainerStats]:
        """Parse raw Docker stats JSON to structured data"""
        try:
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )

            cpu_percent = 0.0
            if system_delta > 0 and cpu_delta > 0:
                num_cpus = len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [1]))
                cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0

            memory_usage = stats["memory_stats"].get("usage", 0)
            memory_limit = stats["memory_stats"].get("limit", 1)
            memory_percent = (memory_usage / memory_limit) * 100.0

            network_rx = sum(
                net.get("rx_bytes", 0) for net in stats.get("networks", {}).values()
            )
            network_tx = sum(
                net.get("tx_bytes", 0) for net in stats.get("networks", {}).values()
            )

            block_read = 0
            block_write = 0
            for entry in stats.get("blkio_stats", {}).get("io_service_bytes_recursive", []):
                if entry.get("op") == "Read":
                    block_read += entry.get("value", 0)
                elif entry.get("op") == "Write":
                    block_write += entry.get("value", 0)

            return ContainerStats(
                cpu_percent=round(cpu_percent, 2),
                memory_usage_bytes=memory_usage,
                memory_limit_bytes=memory_limit,
                memory_percent=round(memory_percent, 2),
                network_rx_bytes=network_rx,
                network_tx_bytes=network_tx,
                block_read_bytes=block_read,
                block_write_bytes=block_write,
                timestamp=datetime.now().isoformat(),
            )
        except Exception:
            return None

    def _parse_health(self, container) -> Optional[dict]:
        """Extract health check status"""
        try:
            health = container.attrs["State"].get("Health")
            if health:
                return {
                    "status": health.get("Status"),
                    "failing_streak": health.get("FailingStreak", 0),
                    "last_check": (
                        health.get("Log", [{}])[-1].get("Start") if health.get("Log") else None
                    ),
                }
        except Exception:
            pass
        return None

    def _parse_ports(self, ports: dict) -> list[dict]:
        """Format port mappings"""
        result = []

        for container_port, bindings in ports.items():
            if bindings:
                for binding in bindings:
                    result.append({
                        "container": container_port,
                        "host_ip": binding.get("HostIp", "0.0.0.0"),
                        "host_port": binding.get("HostPort"),
                    })
            else:
                result.append({"container": container_port, "host_ip": None, "host_port": None})

        return result
