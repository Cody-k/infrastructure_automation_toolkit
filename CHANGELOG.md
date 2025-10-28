# Changelog

## [1.0.0] - 2025-10-27

### Added
- Container management utilities (Docker/Podman health monitoring)
- Resource monitoring (CPU, memory, disk, load average)
- System health checks (failed services, disk space, temperatures)
- Threshold alerting (configurable warning levels)
- Infrastructure monitoring example
- Comprehensive test suite (9 tests)

### Features
- Zero external dependencies (uses system tools)
- Works with Docker or Podman
- Dataclasses for structured data
- Type hints throughout
- Clean, minimal code

### Background
- Patterns from 7-node homelab (11 containers, 6+ weeks uptime)
- Automated monitoring and recovery
- Threshold-based alerting
