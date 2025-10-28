"""Tests for system health checks"""

import pytest
from src.system import SystemHealthCheck, HealthStatus


def test_health_check_initialization():
    """SystemHealthCheck should initialize"""
    checker = SystemHealthCheck()
    assert checker is not None


def test_run_check():
    """Health check should return status"""
    checker = SystemHealthCheck()
    status = checker.run_check()

    assert isinstance(status, HealthStatus)
    assert status.status in ["healthy", "degraded"]
    assert isinstance(status.failed_services, list)
    assert isinstance(status.disk_warnings, list)
