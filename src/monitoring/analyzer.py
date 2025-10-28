"""Resource analyzer | Intelligent analysis with trends, predictions, recommendations"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import statistics
import json


@dataclass
class ResourceTrend:
    """Resource usage trend analysis"""

    current: float
    average: float
    minimum: float
    maximum: float
    trend_direction: str
    volatility: float
    data_points: int
    slope: float


@dataclass
class Prediction:
    """Resource prediction with confidence assessment"""

    resource_name: str
    current_value: float
    predicted_7day: float
    predicted_30day: float
    time_to_90_percent_hours: Optional[float]
    confidence: str
    trend_stable: bool


class ResourceAnalyzer:
    """Intelligent resource analysis with historical tracking and predictions"""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else Path("./data/metrics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.data_dir / "resource_metrics.json"
        self.metrics_history: list[dict] = []
        self.cache: dict = {}
        self.cache_ttl_seconds = 300

    def record_metrics(self, cpu: float, memory: float, disk: float, load: float) -> None:
        """Record current metrics to history"""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu,
            "memory_percent": memory,
            "disk_percent": disk,
            "load_average": load,
        }

        self.metrics_history.append(metric)

        if len(self.metrics_history) > 2000:
            self.metrics_history = self.metrics_history[-1000:]

        self._persist_metrics()

    def analyze_trends(self, hours: int = 24) -> dict[str, ResourceTrend]:
        """Analyze resource trends over time period"""
        cache_key = f"trends_{hours}h"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]

        self._load_metrics()

        if not self.metrics_history:
            return {}

        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [
            m
            for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]

        if len(recent) < 2:
            return {}

        trends = {
            "cpu": self._calculate_trend(recent, "cpu_percent"),
            "memory": self._calculate_trend(recent, "memory_percent"),
            "disk": self._calculate_trend(recent, "disk_percent"),
            "load": self._calculate_trend(recent, "load_average"),
        }

        self.cache[cache_key] = {"data": trends, "timestamp": datetime.now()}
        return trends

    def predict_resource_needs(self) -> dict[str, Prediction]:
        """Alias for predict_resource_exhaustion"""
        return self.predict_resource_exhaustion()

    def predict_resource_exhaustion(self) -> dict[str, Prediction]:
        """Predict when resources will reach critical thresholds"""
        self._load_metrics()

        if len(self.metrics_history) < 10:
            return {}

        predictions = {}

        for resource in ["cpu_percent", "memory_percent", "disk_percent"]:
            values = [m.get(resource, 0) for m in self.metrics_history[-168:]]
            if not values or len(values) < 10:
                continue

            slope = self._linear_regression_slope(values)
            current = values[-1]

            if slope <= 0:
                time_to_90 = None
                pred_7day = current
                pred_30day = current
                stable = True
            else:
                hours_per_datapoint = 1.0
                time_to_90 = ((90.0 - current) / slope) * hours_per_datapoint if slope > 0 else None
                pred_7day = current + (slope * 24 * 7)
                pred_30day = current + (slope * 24 * 30)
                stable = slope < 0.01

            confidence = self._assess_confidence(values)

            predictions[resource] = Prediction(
                resource_name=resource,
                current_value=current,
                predicted_7day=min(pred_7day, 100.0),
                predicted_30day=min(pred_30day, 100.0),
                time_to_90_percent_hours=time_to_90 if time_to_90 and time_to_90 > 0 else None,
                confidence=confidence,
                trend_stable=stable,
            )

        return predictions

    def generate_recommendations(self) -> list[dict]:
        """Generate actionable optimization recommendations"""
        trends = self.analyze_trends(hours=24)
        predictions = self.predict_resource_exhaustion()
        recommendations = []

        for resource, trend in trends.items():
            if trend.current > 90:
                recommendations.append({
                    "resource": resource,
                    "priority": "critical",
                    "action": f"{resource.replace('_', ' ').title()} at {trend.current:.1f}% - immediate action required",
                    "impact": "System stability at risk",
                })
            elif trend.current > 80 and trend.trend_direction == "increasing":
                recommendations.append({
                    "resource": resource,
                    "priority": "high",
                    "action": f"{resource.replace('_', ' ').title()} at {trend.current:.1f}% and rising",
                    "impact": "Will reach critical in days to weeks",
                })
            elif trend.volatility > 15 and trend.current > 50:
                recommendations.append({
                    "resource": resource,
                    "priority": "medium",
                    "action": f"{resource.replace('_', ' ').title()} unstable (volatility {trend.volatility:.1f}%)",
                    "impact": "Unpredictable behavior, investigate cause",
                })

        for resource, pred in predictions.items():
            if pred.time_to_90_percent_hours and pred.time_to_90_percent_hours < 168:
                days = pred.time_to_90_percent_hours / 24
                recommendations.append({
                    "resource": resource,
                    "priority": "high" if days < 7 else "medium",
                    "action": f"{resource.replace('_', ' ').title()} will reach 90% in {days:.1f} days",
                    "impact": f"Plan capacity increase or cleanup (confidence: {pred.confidence})",
                })

        return sorted(
            recommendations,
            key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 4),
        )

    def _calculate_trend(self, metrics: list[dict], field: str) -> ResourceTrend:
        """Calculate comprehensive trend statistics"""
        values = [m.get(field, 0) for m in metrics]

        if not values:
            return ResourceTrend(0, 0, 0, 0, "unknown", 0, 0, 0)

        current = values[-1]
        avg = statistics.mean(values)
        minimum = min(values)
        maximum = max(values)
        slope = self._linear_regression_slope(values)

        direction = (
            "increasing"
            if slope > 0.1
            else "decreasing" if slope < -0.1 else "stable"
        )

        volatility = (statistics.stdev(values) / avg * 100) if len(values) > 1 and avg > 0 else 0

        return ResourceTrend(
            current=current,
            average=avg,
            minimum=minimum,
            maximum=maximum,
            trend_direction=direction,
            volatility=volatility,
            data_points=len(values),
            slope=slope,
        )

    def _linear_regression_slope(self, values: list[float]) -> float:
        """Calculate linear regression slope for trend line"""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))
        y = values

        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        return numerator / denominator if denominator != 0 else 0.0

    def _assess_confidence(self, values: list[float]) -> str:
        """Assess prediction confidence based on data quality"""
        if len(values) < 20:
            return "low"

        if len(values) < 50:
            return "medium"

        try:
            mean_val = statistics.mean(values)
            if mean_val == 0:
                return "low"

            volatility = statistics.stdev(values) / mean_val

            if volatility < 0.1:
                return "high"
            elif volatility < 0.3:
                return "medium"
            else:
                return "low"
        except Exception:
            return "low"

    def _persist_metrics(self) -> None:
        """Save metrics to disk using msgspec for fast serialization"""
        try:
            data = {"metrics": self.metrics_history, "updated": datetime.now().isoformat()}
            with open(self.metrics_file, "wb") as f:
                f.write(json.dumps(data, indent=2).encode())
        except Exception:
            pass

    def _load_metrics(self) -> None:
        """Load metrics from disk"""
        if self.metrics_history:
            return

        try:
            if self.metrics_file.exists():
                with open(self.metrics_file) as f:
                    data = json.load(f)
                    self.metrics_history = data.get("metrics", [])
        except Exception:
            pass

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False

        age = (datetime.now() - self.cache[key]["timestamp"]).seconds
        return age < self.cache_ttl_seconds
