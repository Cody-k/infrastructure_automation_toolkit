"""Tests for alert manager"""

import pytest
from src.alerts import AlertManager, Alert


def test_alert_manager_initialization():
    """AlertManager should initialize"""
    mgr = AlertManager()
    assert mgr.data_dir.exists()
    assert mgr.alerts_file.name == "alerts.json"


def test_create_alert():
    """Should create new alerts"""
    mgr = AlertManager()

    alert = mgr.create_alert(
        alert_type="cpu_high",
        severity="high",
        message="CPU at 90%",
        value=90.0,
        threshold=85.0,
    )

    assert isinstance(alert, Alert)
    assert alert.severity == "high"
    assert alert.acknowledged is False
    assert alert.id.startswith("cpu_high")


def test_duplicate_prevention():
    """Should not create duplicate alerts"""
    mgr = AlertManager()

    alert1 = mgr.create_alert("memory_high", "high", "Memory at 95%", 95.0, 90.0)
    alert2 = mgr.create_alert("memory_high", "high", "Memory at 96%", 96.0, 90.0)

    assert alert1.id == alert2.id


def test_acknowledge_alert():
    """Should acknowledge alerts"""
    mgr = AlertManager()

    alert = mgr.create_alert("disk_high", "medium", "Disk at 80%", 80.0, 75.0)
    result = mgr.acknowledge_alert(alert.id)

    assert result is True
    assert alert.acknowledged is True


def test_get_active_alerts():
    """Should filter active alerts"""
    mgr = AlertManager()

    mgr.create_alert("test1", "low", "Test 1", 10.0, 5.0)
    mgr.create_alert("test2", "high", "Test 2", 90.0, 85.0)
    mgr.create_alert("test3", "critical", "Test 3", 95.0, 90.0)

    all_active = mgr.get_active_alerts()
    assert len(all_active) >= 3

    high_only = mgr.get_active_alerts(min_severity="high")
    assert all(a.severity in ["high", "critical"] for a in high_only)


def test_clear_acknowledged():
    """Should remove acknowledged alerts"""
    mgr = AlertManager()

    alert = mgr.create_alert("test_clear", "low", "Test", 10.0, 5.0)
    mgr.acknowledge_alert(alert.id)

    removed = mgr.clear_acknowledged()
    assert removed >= 1


def test_alert_persistence():
    """Alerts should persist across instances"""
    mgr1 = AlertManager()
    alert = mgr1.create_alert("persist_test", "medium", "Persistence test", 50.0, 40.0)

    mgr2 = AlertManager()
    loaded_alerts = mgr2.get_active_alerts()

    assert any(a.id == alert.id for a in loaded_alerts)
