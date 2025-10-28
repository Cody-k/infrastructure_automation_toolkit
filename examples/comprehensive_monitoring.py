"""Comprehensive monitoring | Complete infrastructure analysis workflow"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import DockerManager, ResourceAnalyzer, ResourceOptimizer
from src.monitoring import ResourceTrend


def main():
    """Demonstrate comprehensive infrastructure monitoring"""

    print("=== Comprehensive Infrastructure Analysis ===\n")

    docker = DockerManager()
    analyzer = ResourceAnalyzer()
    optimizer = ResourceOptimizer()

    print("Docker Container Analysis...")
    containers = docker.list_all(include_stopped=True)
    running = [c for c in containers if c.status == "running"]

    print(f"  Total containers: {len(containers)}")
    print(f"  Running: {len(running)}")
    print(f"  Stopped: {len(containers) - len(running)}\n")

    if running:
        print("Resource hogs (>80% CPU or memory):")
        hogs = docker.identify_resource_hogs(threshold_cpu=80.0, threshold_mem=80.0)
        if hogs:
            for hog in hogs:
                print(f"  ⚠ {hog['name']}: CPU {hog['cpu_percent']:.1f}%, Mem {hog['memory_percent']:.1f}%")
        else:
            print("  ✓ No resource hogs detected")
        print()

        print("Container Health Status:")
        for container in running[:10]:
            health_icon = "✓" if container.health in ["healthy", "no_healthcheck"] else "✗"
            print(f"  {health_icon} {container.name}: {container.health}")
    print()

    print("Resource Trend Analysis (24 hours)...")
    trends = analyzer.analyze_trends(hours=24)

    if trends:
        for resource, trend in trends.items():
            arrow = "↑" if trend.trend_direction == "increasing" else "↓" if trend.trend_direction == "decreasing" else "→"
            print(f"  {resource.upper()}: {trend.current:.1f}% {arrow} (avg: {trend.average:.1f}%, range: {trend.minimum:.1f}-{trend.maximum:.1f}%)")
    else:
        print("  No historical data (run continuously to build trends)")
    print()

    print("Predictive Analysis...")
    predictions = analyzer.predict_resource_needs()

    if predictions:
        for resource, pred in predictions.items():
            print(f"  {resource.upper()}:")
            print(f"    Predicted (7 days): {pred.predicted_value:.1f}%")
            if pred.time_to_threshold:
                print(f"    Time to 90%: {pred.time_to_threshold/24:.1f} days")
            print(f"    Confidence: {pred.confidence}")
            print(f"    Action: {pred.recommendation}")
    else:
        print("  Insufficient data for predictions (need 10+ data points)")
    print()

    print("Optimization Recommendations...")
    system_metrics = {
        "memory_percent": trends.get("memory", ResourceTrend(0, 0, 0, 0, "", 0, 0)).current if trends else 0,
        "disk_percent": trends.get("disk", ResourceTrend(0, 0, 0, 0, "", 0, 0)).current if trends else 0,
    }

    recommendations = optimizer.generate_all_recommendations(containers, system_metrics)

    if recommendations:
        for rec in recommendations:
            priority_icon = "🔴" if rec.priority == "high" else "🟡" if rec.priority == "medium" else "🟢"
            print(f"  {priority_icon} [{rec.priority.upper()}] {rec.action}")
            print(f"     Impact: {rec.impact}")
    else:
        print("  ✓ No immediate optimizations needed")

    print("\n=== Analysis Complete ===")
    print("Run periodically to build historical trends for predictions.")


if __name__ == "__main__":
    main()
