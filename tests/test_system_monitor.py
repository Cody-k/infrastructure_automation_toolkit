"""Tests for system monitor"""

import pytest
from src.monitoring import SystemMonitor, SystemMetrics


def test_system_monitor_initialization():
    """SystemMonitor should initialize with psutil"""
    monitor = SystemMonitor()
    assert monitor.data_dir.exists()
    assert monitor.metrics_file.name == "system_metrics.json"


def test_collect_metrics():
    """Should collect comprehensive system metrics"""
    monitor = SystemMonitor()
    metrics = monitor.collect_metrics()

    assert isinstance(metrics, SystemMetrics)
    assert metrics.cpu_percent >= 0
    assert metrics.cpu_count > 0
    assert metrics.memory_percent >= 0
    assert metrics.memory_total_gb > 0
    assert metrics.disk_percent >= 0
    assert metrics.process_count > 0
    assert metrics.uptime_hours >= 0


def test_process_details():
    """Should get top processes"""
    monitor = SystemMonitor()
    processes = monitor.get_process_details(limit=5)

    assert "by_cpu" in processes
    assert "by_memory" in processes
    assert len(processes["by_cpu"]) <= 5
    assert len(processes["by_memory"]) <= 5


def test_disk_partitions():
    """Should list disk partitions"""
    monitor = SystemMonitor()
    partitions = monitor.get_disk_partitions()

    assert isinstance(partitions, list)
    if partitions:
        assert "mountpoint" in partitions[0]
        assert "percent" in partitions[0]


def test_threshold_warnings():
    """Should generate warnings for high resource usage"""
    monitor = SystemMonitor()
    metrics = monitor.collect_metrics()

    warnings = monitor.check_thresholds(metrics)
    assert isinstance(warnings, list)

    for warning in warnings:
        assert "severity" in warning
        assert warning["severity"] in ["high", "critical"]
        assert warning["value"] > warning["threshold"]


def test_metrics_persistence():
    """Should persist and load metrics"""
    monitor = SystemMonitor()
    metrics = monitor.collect_metrics()

    monitor.persist_metrics(metrics)

    assert monitor.metrics_file.exists()
