"""Infrastructure monitoring | Complete monitoring workflow"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ContainerManager, ResourceMonitor, SystemHealthCheck


def main():
    """Demonstrate infrastructure monitoring"""

    print("=== Infrastructure Monitoring Demo ===\n")

    print("System Health Check...")
    health = SystemHealthCheck()
    status = health.run_check()

    print(f"Status: {status.status.upper()}\n")

    if status.failed_services:
        print(f"Failed Services ({len(status.failed_services)}):")
        for service in status.failed_services[:5]:
            print(f"  ✗ {service}")
        print()

    if status.disk_warnings:
        print("Disk Warnings:")
        for warning in status.disk_warnings:
            print(f"  ⚠ {warning}")
        print()

    print("Resource Metrics...")
    monitor = ResourceMonitor()
    metrics = monitor.get_metrics()

    if metrics:
        print(f"  CPU: {metrics.cpu_percent:.1f}%")
        print(f"  Memory: {metrics.memory_percent:.1f}% ({metrics.memory_available_gb:.1f} GB available)")
        print(f"  Disk: {metrics.disk_percent:.1f}% ({metrics.disk_available_gb:.1f} GB available)")
        print(f"  Load: {metrics.load_average_1min:.2f}\n")

        warnings = monitor.check_thresholds(metrics)
        if warnings:
            print("Resource Warnings:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
        else:
            print("✓ All resources within normal thresholds")
    print()

    print("Container Status...")
    manager = ContainerManager()

    if manager.available:
        containers = manager.list_containers()
        print(f"Running containers: {len(containers)}\n")

        for container in containers[:10]:
            health = manager.health_check(container.name)
            health_status = health.get("health", "unknown")
            status_icon = "✓" if health_status in ["healthy", "no_healthcheck"] else "✗"
            print(f"  {status_icon} {container.name}: {container.state} ({health_status})")

        unhealthy = manager.restart_unhealthy(dry_run=True)
        if unhealthy:
            print(f"\nUnhealthy containers (would restart):")
            for name in unhealthy:
                print(f"  → {name}")
    else:
        print("Docker/Podman not available")

    print("\n=== Demo Complete ===")
    print("Production use: Run on cron for automated monitoring")


if __name__ == "__main__":
    main()
