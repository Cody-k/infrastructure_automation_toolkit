"""Tests for resource optimizer"""

import pytest
from src.analysis import ResourceOptimizer, Optimization


def test_optimizer_initialization():
    """ResourceOptimizer should initialize"""
    optimizer = ResourceOptimizer()
    assert optimizer is not None


def test_analyze_memory_usage():
    """Should generate memory optimization recommendations"""
    optimizer = ResourceOptimizer()

    high_memory = optimizer.analyze_memory_usage(memory_percent=90.0, available_gb=5.0)
    assert len(high_memory) > 0
    assert high_memory[0].priority == "high"

    normal_memory = optimizer.analyze_memory_usage(memory_percent=50.0, available_gb=20.0)
    assert len(normal_memory) == 0


def test_analyze_disk_usage():
    """Should generate disk optimization recommendations"""
    optimizer = ResourceOptimizer()

    critical_disk = optimizer.analyze_disk_usage(disk_percent=95.0, available_gb=10.0)
    assert len(critical_disk) > 0
    assert critical_disk[0].priority == "high"

    normal_disk = optimizer.analyze_disk_usage(disk_percent=50.0, available_gb=200.0)
    assert len(normal_disk) == 0


def test_generate_all_recommendations():
    """Should aggregate all optimization recommendations"""
    optimizer = ResourceOptimizer()

    system_metrics = {
        "memory_percent": 85.0,
        "memory_available_gb": 10.0,
        "disk_percent": 92.0,
        "disk_available_gb": 20.0,
    }

    recommendations = optimizer.generate_all_recommendations([], system_metrics)
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    priorities = [r.priority for r in recommendations]
    assert priorities == sorted(priorities, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x])
