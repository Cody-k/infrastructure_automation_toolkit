"""Resource analyzer | Trend analysis, predictions, and optimization recommendations"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import statistics
import subprocess


@dataclass
class ResourceTrend:
    """Resource usage trend over time"""

    current: float
    average: float
    minimum: float
    maximum: float
    trend_direction: str
    volatility: float
    data_points: int


@dataclass
class Prediction:
    """Resource prediction with confidence"""

    predicted_value: float
    time_to_threshold: Optional[float]
    confidence: str
    recommendation: str


class ResourceAnalyzer:
    """Intelligent resource analysis with trends and predictions"""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else Path("./data/metrics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_history: list[dict] = []

    def analyze_trends(self, hours: int = 24) -> dict[str, ResourceTrend]:
        """Analyze resource usage trends over time period"""
        self._load_metrics(hours)

        if not self.metrics_history:
            return {}

        return {
            "cpu": self._calculate_trend("cpu_percent"),
            "memory": self._calculate_trend("memory_percent"),
            "disk": self._calculate_trend("disk_percent"),
        }

    def predict_resource_needs(self) -> dict[str, Prediction]:
        """Predict when resources will reach critical thresholds"""
        self._load_metrics(hours=168)

        if len(self.metrics_history) < 10:
            return {}

        predictions = {}

        for resource in ["cpu_percent", "memory_percent", "disk_percent"]:
            values = [m.get(resource, 0) for m in self.metrics_history]
            if not values:
                continue

            trend_slope = self._linear_regression_slope(values)
            current = values[-1]
            threshold = 90.0 if resource != "cpu_percent" else 85.0

            if trend_slope > 0.01:
                hours_to_threshold = (threshold - current) / (trend_slope * 24)
                confidence = self._calculate_confidence(values)

                predictions[resource] = Prediction(
                    predicted_value=current + (trend_slope * 24 * 7),
                    time_to_threshold=hours_to_threshold if hours_to_threshold > 0 else None,
                    confidence=confidence,
                    recommendation=self._generate_recommendation(resource, hours_to_threshold),
                )

        return predictions

    def generate_recommendations(self) -> list[dict[str, str]]:
        """Generate actionable optimization recommendations"""
        trends = self.analyze_trends(hours=24)
        recommendations = []

        for resource, trend in trends.items():
            if trend.current > 85:
                recommendations.append({
                    "resource": resource,
                    "priority": "high",
                    "action": f"Immediate: {resource.replace('_', ' ')} at {trend.current:.1f}%",
                })
            elif trend.trend_direction == "increasing" and trend.current > 70:
                recommendations.append({
                    "resource": resource,
                    "priority": "medium",
                    "action": f"Monitor: {resource.replace('_', ' ')} trending up ({trend.average:.1f}% avg)",
                })

        return recommendations

    def _calculate_trend(self, metric_name: str) -> ResourceTrend:
        """Calculate trend statistics for metric"""
        values = [m.get(metric_name, 0) for m in self.metrics_history if metric_name in m]

        if not values:
            return ResourceTrend(0, 0, 0, 0, "unknown", 0, 0)

        current = values[-1]
        avg = statistics.mean(values)
        minimum = min(values)
        maximum = max(values)

        slope = self._linear_regression_slope(values)
        direction = "increasing" if slope > 0.1 else "decreasing" if slope < -0.1 else "stable"

        volatility = statistics.stdev(values) if len(values) > 1 else 0.0

        return ResourceTrend(
            current=current,
            average=avg,
            minimum=minimum,
            maximum=maximum,
            trend_direction=direction,
            volatility=volatility,
            data_points=len(values),
        )

    def _linear_regression_slope(self, values: list[float]) -> float:
        """Calculate linear regression slope"""
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

    def _calculate_confidence(self, values: list[float]) -> str:
        """Calculate prediction confidence based on data quality"""
        if len(values) < 10:
            return "low"

        volatility = statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) > 0 else 1.0

        if volatility < 0.1:
            return "high"
        elif volatility < 0.3:
            return "medium"
        else:
            return "low"

    def _generate_recommendation(self, resource: str, hours_to_threshold: Optional[float]) -> str:
        """Generate recommendation based on prediction"""
        if not hours_to_threshold or hours_to_threshold < 0:
            return "Monitor usage patterns"

        days = hours_to_threshold / 24

        if days < 7:
            return f"Critical: {resource} will reach threshold in {days:.1f} days"
        elif days < 30:
            return f"Plan cleanup: {resource} threshold in {days:.0f} days"
        else:
            return f"Monitor: {resource} stable for ~{days:.0f} days"

    def _load_metrics(self, hours: int):
        """Load metrics from data directory"""
        self.metrics_history = []

        try:
            result = subprocess.run(
                ["free", "-m"],
                capture_output=True,
                text=True,
                check=True,
            )
            lines = result.stdout.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 3:
                    total = float(parts[1])
                    used = float(parts[2])
                    self.metrics_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "memory_percent": (used / total) * 100 if total > 0 else 0,
                    })
        except Exception:
            pass

        try:
            result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, check=True)
            lines = result.stdout.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    percent_str = parts[4].rstrip("%")
                    self.metrics_history[0]["disk_percent"] = float(percent_str)
        except Exception:
            pass

        try:
            result = subprocess.run(["top", "-bn1"], capture_output=True, text=True, timeout=2)
            for line in result.stdout.split("\n"):
                if "Cpu(s)" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "id" in part and i > 0:
                            idle = float(parts[i - 1])
                            if self.metrics_history:
                                self.metrics_history[0]["cpu_percent"] = 100.0 - idle
        except Exception:
            pass
