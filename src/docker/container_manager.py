"""Container management | Docker/Podman health monitoring and operations"""

from dataclasses import dataclass
from typing import Optional
import subprocess
import json


@dataclass
class ContainerStatus:
    """Container status information"""

    name: str
    state: str
    image: str
    cpu_percent: float
    memory_mb: float
    uptime_hours: float


class ContainerManager:
    """Manage Docker/Podman containers with health monitoring"""

    def __init__(self, runtime: str = "docker"):
        self.runtime = runtime
        self.available = self._check_available()

    def list_containers(self, all: bool = False) -> list[ContainerStatus]:
        """List running containers with resource usage"""
        if not self.available:
            return []

        cmd = [self.runtime, "ps", "--format", "json"]
        if all:
            cmd.append("-a")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            containers = []

            for line in result.stdout.strip().split("\n"):
                if line:
                    data = json.loads(line)
                    containers.append(
                        ContainerStatus(
                            name=data.get("Names", ""),
                            state=data.get("State", ""),
                            image=data.get("Image", ""),
                            cpu_percent=0.0,
                            memory_mb=0.0,
                            uptime_hours=0.0,
                        )
                    )

            return containers
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []

    def get_stats(self, container_name: str) -> Optional[dict]:
        """Get resource statistics for container"""
        if not self.available:
            return None

        cmd = [self.runtime, "stats", container_name, "--no-stream", "--format", "json"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired):
            return None

    def health_check(self, container_name: str) -> dict[str, str]:
        """Check container health status"""
        if not self.available:
            return {"status": "runtime_unavailable"}

        cmd = [self.runtime, "inspect", container_name, "--format", "{{.State.Health.Status}}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            health = result.stdout.strip()
            return {"container": container_name, "health": health if health else "no_healthcheck"}
        except subprocess.CalledProcessError:
            return {"container": container_name, "health": "not_found"}

    def restart_unhealthy(self, dry_run: bool = True) -> list[str]:
        """Restart containers that failed health checks"""
        containers = self.list_containers()
        restarted = []

        for container in containers:
            health = self.health_check(container.name)
            if health.get("health") == "unhealthy":
                if not dry_run:
                    try:
                        subprocess.run(
                            [self.runtime, "restart", container.name],
                            check=True,
                            capture_output=True,
                        )
                        restarted.append(container.name)
                    except subprocess.CalledProcessError:
                        pass
                else:
                    restarted.append(f"{container.name} (dry-run)")

        return restarted

    def _check_available(self) -> bool:
        """Check if Docker/Podman is available"""
        try:
            subprocess.run(
                [self.runtime, "ps"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
