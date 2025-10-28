"""Complete workflow | Full infrastructure monitoring and analysis"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import (
    DockerManager,
    ResourceAnalyzer,
    SystemMonitor,
    ResourceOptimizer,
    AlertManager,
)


def main():
    """Demonstrate complete infrastructure automation workflow"""

    print("=== Complete Infrastructure Automation Workflow ===\n")

    print("[1/5] Collecting System Metrics...")
    monitor = SystemMonitor()
    metrics = monitor.collect_metrics()

    print(f"  CPU: {metrics.cpu_percent:.1f}% ({metrics.cpu_count} cores, load: {metrics.load_avg_1m:.2f})")
    print(f"  Memory: {metrics.memory_percent:.1f}% ({metrics.memory_available_gb:.1f} GB free)")
    print(f"  Disk: {metrics.disk_percent:.1f}% ({metrics.disk_free_gb:.1f} GB free)")
    print(f"  Network: ↑{metrics.network_sent_mb:.1f} MB ↓{metrics.network_recv_mb:.1f} MB")
    print(f"  Uptime: {metrics.uptime_hours:.1f} hours\n")

    print("[2/5] Analyzing Containers...")
    docker = DockerManager()

    if docker.available:
        containers = docker.list_all()
        running = [c for c in containers if c.status == "running"]
        print(f"  Containers: {len(running)} running, {len(containers) - len(running)} stopped")

        hogs = docker.identify_resource_hogs(cpu_threshold=70.0, memory_threshold=70.0)
        if hogs:
            print(f"  Resource hogs:")
            for hog in hogs:
                print(f"    - {hog['name']}: CPU {hog['cpu_percent']:.1f}%, Mem {hog['memory_percent']:.1f}%")
        else:
            print(f"  ✓ No resource hogs")
    else:
        print("  Docker not available")
    print()

    print("[3/5] Trend Analysis...")
    analyzer = ResourceAnalyzer()
    analyzer.record_metrics(
        cpu=metrics.cpu_percent,
        memory=metrics.memory_percent,
        disk=metrics.disk_percent,
        load=metrics.load_avg_1m,
    )

    trends = analyzer.analyze_trends(hours=24)
    if trends:
        for name, trend in trends.items():
            arrow = "↑" if trend.trend_direction == "increasing" else "↓" if trend.trend_direction == "decreasing" else "→"
            print(f"  {name.upper()}: {trend.current:.1f}% {arrow} (volatility: {trend.volatility:.1f}%)")
    else:
        print("  No historical data (run multiple times to build trends)")
    print()

    print("[4/5] Predictive Forecasting...")
    predictions = analyzer.predict_resource_exhaustion()
    if predictions:
        for name, pred in predictions.items():
            print(f"  {name.upper()}:")
            print(f"    7-day forecast: {pred.predicted_7day:.1f}%")
            if pred.time_to_90_percent_hours:
                print(f"    Time to 90%: {pred.time_to_90_percent_hours/24:.1f} days")
            print(f"    Confidence: {pred.confidence}")
    else:
        print("  Insufficient data (need 10+ data points)")
    print()

    print("[5/5] Generating Recommendations...")
    optimizer = ResourceOptimizer()
    system_dict = {
        "memory_percent": metrics.memory_percent,
        "memory_available_gb": metrics.memory_available_gb,
        "disk_percent": metrics.disk_percent,
        "disk_available_gb": metrics.disk_free_gb,
    }

    recommendations = optimizer.generate_all_recommendations(containers if docker.available else [], system_dict)

    if recommendations:
        for rec in recommendations:
            icon = "🔴" if rec.priority == "critical" else "🟡" if rec.priority == "high" else "🟢"
            print(f"  {icon} [{rec.priority.upper()}] {rec.action}")
    else:
        print("  ✓ No optimization recommendations")
    print()

    print("=== Alert System ===\n")
    alert_mgr = AlertManager()

    threshold_warnings = monitor.check_thresholds(metrics)
    for warning in threshold_warnings:
        alert = alert_mgr.create_alert(
            alert_type=warning["metric"],
            severity=warning["severity"],
            message=warning["message"],
            value=warning["value"],
            threshold=warning["threshold"],
        )
        print(f"  🚨 [{alert.severity.upper()}] {alert.message}")

    active = alert_mgr.get_active_alerts()
    if not threshold_warnings:
        print(f"  Active alerts: {len(active)}")

    print("\n=== Workflow Complete ===")
    print(f"Metrics persisted to: {monitor.metrics_file}")
    print(f"Alerts persisted to: {alert_mgr.alerts_file}")
    print("Run periodically for trend tracking and predictions.")


if __name__ == "__main__":
    main()
