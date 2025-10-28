"""Alert manager | Severity-based alerting system"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import json


@dataclass
class Alert:
    """Alert with severity and acknowledgment"""

    id: str
    type: str
    severity: str
    message: str
    value: float
    threshold: float
    created: str
    acknowledged: bool = False


class AlertManager:
    """Manage alerts with persistence and deduplication"""

    SEVERITY_LEVELS = ["info", "low", "medium", "high", "critical"]

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else Path("./data/alerts")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.alerts_file = self.data_dir / "alerts.json"
        self.active_alerts: list[Alert] = []
        self._load_alerts()

    def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        value: float,
        threshold: float,
    ) -> Alert:
        """Create new alert if not duplicate"""
        alert_id = f"{alert_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        existing = [a for a in self.active_alerts if a.type == alert_type and not a.acknowledged]

        if existing:
            return existing[0]

        alert = Alert(
            id=alert_id,
            type=alert_type,
            severity=severity,
            message=message,
            value=value,
            threshold=threshold,
            created=datetime.now().isoformat(),
            acknowledged=False,
        )

        self.active_alerts.append(alert)
        self._persist_alerts()

        return alert

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert to prevent repeat notifications"""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                self._persist_alerts()
                return True
        return False

    def get_active_alerts(self, min_severity: Optional[str] = None) -> list[Alert]:
        """Get unacknowledged alerts, optionally filtered by severity"""
        alerts = [a for a in self.active_alerts if not a.acknowledged]

        if min_severity:
            min_level = self.SEVERITY_LEVELS.index(min_severity)
            alerts = [
                a
                for a in alerts
                if self.SEVERITY_LEVELS.index(a.severity) >= min_level
            ]

        return sorted(
            alerts,
            key=lambda x: (
                self.SEVERITY_LEVELS.index(x.severity),
                x.created,
            ),
            reverse=True,
        )

    def clear_acknowledged(self) -> int:
        """Remove acknowledged alerts"""
        original_count = len(self.active_alerts)
        self.active_alerts = [a for a in self.active_alerts if not a.acknowledged]
        removed = original_count - len(self.active_alerts)

        if removed > 0:
            self._persist_alerts()

        return removed

    def clear_old_alerts(self, hours: int = 24) -> int:
        """Remove alerts older than specified hours"""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        original_count = len(self.active_alerts)

        self.active_alerts = [
            a
            for a in self.active_alerts
            if datetime.fromisoformat(a.created).timestamp() > cutoff
        ]

        removed = original_count - len(self.active_alerts)

        if removed > 0:
            self._persist_alerts()

        return removed

    def _persist_alerts(self) -> None:
        """Save alerts to disk"""
        try:
            data = {
                "alerts": [
                    {
                        "id": a.id,
                        "type": a.type,
                        "severity": a.severity,
                        "message": a.message,
                        "value": a.value,
                        "threshold": a.threshold,
                        "created": a.created,
                        "acknowledged": a.acknowledged,
                    }
                    for a in self.active_alerts
                ],
                "updated": datetime.now().isoformat(),
            }

            with open(self.alerts_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load_alerts(self) -> None:
        """Load alerts from disk"""
        try:
            if self.alerts_file.exists():
                with open(self.alerts_file) as f:
                    data = json.load(f)
                    self.active_alerts = [
                        Alert(
                            id=a["id"],
                            type=a["type"],
                            severity=a["severity"],
                            message=a["message"],
                            value=a["value"],
                            threshold=a["threshold"],
                            created=a["created"],
                            acknowledged=a.get("acknowledged", False),
                        )
                        for a in data.get("alerts", [])
                    ]
        except Exception:
            pass
