"""Tests for container management"""

import pytest
from src.docker import ContainerManager, ContainerStatus


def test_container_manager_initialization():
    """ContainerManager should initialize"""
    manager = ContainerManager()
    assert manager.runtime in ["docker", "podman"]


def test_list_containers():
    """Should list containers or return empty list"""
    manager = ContainerManager()
    containers = manager.list_containers()

    assert isinstance(containers, list)
    if containers:
        assert isinstance(containers[0], ContainerStatus)


def test_health_check():
    """Health check should return dict"""
    manager = ContainerManager()
    result = manager.health_check("nonexistent_container")

    assert isinstance(result, dict)
    assert "container" in result or "health" in result


def test_restart_dry_run():
    """Dry run should return list without actually restarting"""
    manager = ContainerManager()
    restarted = manager.restart_unhealthy(dry_run=True)

    assert isinstance(restarted, list)
