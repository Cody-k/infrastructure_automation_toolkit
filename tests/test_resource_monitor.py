"""Tests for resource monitoring"""

import pytest
from src.monitoring import ResourceMonitor, SystemMetrics


def test_resource_monitor_initialization():
    """ResourceMonitor should initialize"""
    monitor = ResourceMonitor()
    assert monitor is not None


def test_get_metrics():
    """Should return metrics or None"""
    monitor = ResourceMonitor()
    metrics = monitor.get_metrics()

    if metrics:
        assert isinstance(metrics, SystemMetrics)
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0
        assert metrics.disk_percent >= 0


def test_threshold_checking():
    """Should identify metrics exceeding thresholds"""
    monitor = ResourceMonitor()

    high_cpu = SystemMetrics(
        cpu_percent=95.0,
        memory_percent=50.0,
        memory_available_gb=10.0,
        disk_percent=50.0,
        disk_available_gb=100.0,
        load_average_1min=2.0,
    )

    warnings = monitor.check_thresholds(high_cpu)
    assert len(warnings) > 0
    assert any("CPU" in w for w in warnings)


def test_threshold_normal():
    """Should return no warnings for normal metrics"""
    monitor = ResourceMonitor()

    normal = SystemMetrics(
        cpu_percent=30.0,
        memory_percent=50.0,
        memory_available_gb=20.0,
        disk_percent=50.0,
        disk_available_gb=200.0,
        load_average_1min=2.0,
    )

    warnings = monitor.check_thresholds(normal)
    assert len(warnings) == 0
