"""Tests for Docker manager"""

import pytest
from src.docker import DockerManager, ContainerInfo, ContainerStats


def test_docker_manager_initialization():
    """DockerManager should initialize"""
    manager = DockerManager()
    assert manager.runtime in ["docker", "podman"]
    assert isinstance(manager.available, bool)


def test_list_containers():
    """Should list containers or return empty list"""
    manager = DockerManager()
    containers = manager.list_all()

    assert isinstance(containers, list)
    if containers:
        assert isinstance(containers[0], ContainerInfo)
        assert hasattr(containers[0], "name")
        assert hasattr(containers[0], "status")


def test_get_stats():
    """Stats should return ContainerStats or None"""
    manager = DockerManager()
    containers = manager.list_all(include_stopped=False)

    if containers:
        stats = manager.get_stats(containers[0].name)
        if stats:
            assert isinstance(stats, ContainerStats)
            assert stats.cpu_percent >= 0
            assert stats.memory_percent >= 0


def test_identify_resource_hogs():
    """Should identify high-resource containers"""
    manager = DockerManager()
    hogs = manager.identify_resource_hogs(threshold_cpu=80.0, threshold_mem=80.0)

    assert isinstance(hogs, list)
    for hog in hogs:
        assert "name" in hog
        assert hog["cpu_percent"] > 80 or hog["memory_percent"] > 80
