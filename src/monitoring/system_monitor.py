"""System monitor | Real-time metrics collection with psutil"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class SystemMetrics:
    """Complete system metrics snapshot"""

    timestamp: str
    cpu_percent: float
    cpu_count: int
    load_avg_1m: float
    load_avg_5m: float
    load_avg_15m: float
    memory_percent: float
    memory_total_gb: float
    memory_available_gb: float
    swap_percent: float
    disk_percent: float
    disk_total_gb: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    uptime_hours: float


class SystemMonitor:
    """Collect comprehensive system metrics using psutil"""

    def __init__(self, data_dir: Optional[Path] = None):
        if not PSUTIL_AVAILABLE:
            raise ImportError("psutil required: pip install psutil")

        self.data_dir = Path(data_dir) if data_dir else Path("./data/metrics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.data_dir / "system_metrics.json"

    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=False) or 1

        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage("/")
        network = psutil.net_io_counters()

        load_avg = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0, 0, 0)

        boot_time = psutil.boot_time()
        uptime = datetime.now().timestamp() - boot_time

        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            load_avg_1m=load_avg[0],
            load_avg_5m=load_avg[1],
            load_avg_15m=load_avg[2],
            memory_percent=memory.percent,
            memory_total_gb=memory.total / (1024**3),
            memory_available_gb=memory.available / (1024**3),
            swap_percent=swap.percent,
            disk_percent=disk.percent,
            disk_total_gb=disk.total / (1024**3),
            disk_free_gb=disk.free / (1024**3),
            network_sent_mb=network.bytes_sent / (1024**2),
            network_recv_mb=network.bytes_recv / (1024**2),
            process_count=len(psutil.pids()),
            uptime_hours=uptime / 3600,
        )

    def get_process_details(self, limit: int = 10) -> dict:
        """Get top processes by CPU and memory"""
        processes = []

        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        by_cpu = sorted(processes, key=lambda x: x.get("cpu_percent") or 0, reverse=True)[:limit]
        by_memory = sorted(processes, key=lambda x: x.get("memory_percent") or 0, reverse=True)[:limit]

        return {
            "by_cpu": by_cpu,
            "by_memory": by_memory,
            "total_processes": len(processes),
        }

    def get_disk_partitions(self) -> list[dict]:
        """Get disk usage for all partitions"""
        partitions = []

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": usage.total / (1024**3),
                    "used_gb": usage.used / (1024**3),
                    "free_gb": usage.free / (1024**3),
                    "percent": usage.percent,
                })
            except (PermissionError, OSError):
                pass

        return partitions

    def check_thresholds(self, metrics: SystemMetrics) -> list[dict]:
        """Check if metrics exceed warning thresholds"""
        warnings = []

        if metrics.cpu_percent > 85:
            warnings.append({
                "metric": "cpu",
                "severity": "high",
                "value": metrics.cpu_percent,
                "threshold": 85.0,
                "message": f"CPU usage at {metrics.cpu_percent:.1f}%",
            })

        if metrics.memory_percent > 90:
            warnings.append({
                "metric": "memory",
                "severity": "critical",
                "value": metrics.memory_percent,
                "threshold": 90.0,
                "message": f"Memory at {metrics.memory_percent:.1f}% ({metrics.memory_available_gb:.1f} GB free)",
            })
        elif metrics.memory_percent > 80:
            warnings.append({
                "metric": "memory",
                "severity": "high",
                "value": metrics.memory_percent,
                "threshold": 80.0,
                "message": f"Memory at {metrics.memory_percent:.1f}%",
            })

        if metrics.disk_percent > 90:
            warnings.append({
                "metric": "disk",
                "severity": "critical",
                "value": metrics.disk_percent,
                "threshold": 90.0,
                "message": f"Disk at {metrics.disk_percent:.1f}% ({metrics.disk_free_gb:.1f} GB free)",
            })
        elif metrics.disk_percent > 85:
            warnings.append({
                "metric": "disk",
                "severity": "high",
                "value": metrics.disk_percent,
                "threshold": 85.0,
                "message": f"Disk at {metrics.disk_percent:.1f}%",
            })

        if metrics.load_avg_1m > metrics.cpu_count * 2:
            warnings.append({
                "metric": "load",
                "severity": "high",
                "value": metrics.load_avg_1m,
                "threshold": metrics.cpu_count * 2,
                "message": f"Load average {metrics.load_avg_1m:.2f} (>{metrics.cpu_count * 2} cores)",
            })

        return warnings

    def persist_metrics(self, metrics: SystemMetrics) -> None:
        """Save current metrics to persistent storage"""
        try:
            data = {"metrics": [], "updated": datetime.now().isoformat()}

            if self.metrics_file.exists():
                with open(self.metrics_file) as f:
                    existing = json.load(f)
                    data["metrics"] = existing.get("metrics", [])

            metric_dict = {
                "timestamp": metrics.timestamp,
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_percent": metrics.disk_percent,
                "load_average": metrics.load_avg_1m,
            }

            data["metrics"].append(metric_dict)

            if len(data["metrics"]) > 2000:
                data["metrics"] = data["metrics"][-1000:]

            with open(self.metrics_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception:
            pass
