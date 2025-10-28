"""Tests for resource analyzer"""

import pytest
from src.monitoring import ResourceAnalyzer, ResourceTrend, Prediction


def test_analyzer_initialization():
    """ResourceAnalyzer should initialize"""
    analyzer = ResourceAnalyzer()
    assert analyzer.data_dir.exists()


def test_record_and_analyze():
    """Should record metrics and analyze trends"""
    analyzer = ResourceAnalyzer()

    for i in range(25):
        analyzer.record_metrics(cpu=50 + i, memory=60 + i * 0.5, disk=70, load=2.0)

    trends = analyzer.analyze_trends(hours=24)

    assert "cpu" in trends
    assert "memory" in trends
    assert isinstance(trends["cpu"], ResourceTrend)
    assert trends["cpu"].data_points == 25
    assert trends["cpu"].trend_direction == "increasing"


def test_prediction_generation():
    """Should generate predictions with confidence"""
    analyzer = ResourceAnalyzer()

    for i in range(50):
        analyzer.record_metrics(cpu=40 + i * 0.5, memory=50 + i * 0.3, disk=60, load=2.0)

    predictions = analyzer.predict_resource_exhaustion()

    assert "cpu_percent" in predictions or "memory_percent" in predictions
    if predictions:
        for pred in predictions.values():
            assert isinstance(pred, Prediction)
            assert pred.confidence in ["high", "medium", "low"]


def test_recommendation_generation():
    """Should generate actionable recommendations"""
    analyzer = ResourceAnalyzer()

    for i in range(10):
        analyzer.record_metrics(cpu=85, memory=92, disk=88, load=5.0)

    recommendations = analyzer.generate_recommendations()

    assert len(recommendations) > 0
    for rec in recommendations:
        assert rec["priority"] in ["critical", "high", "medium", "low"]
        assert len(rec["action"]) > 0


def test_linear_regression():
    """Linear regression should calculate correct slope"""
    analyzer = ResourceAnalyzer()

    increasing = [10, 20, 30, 40, 50]
    slope_inc = analyzer._linear_regression_slope(increasing)
    assert slope_inc > 5

    decreasing = [50, 40, 30, 20, 10]
    slope_dec = analyzer._linear_regression_slope(decreasing)
    assert slope_dec < -5

    flat = [50, 50, 50, 50, 50]
    slope_flat = analyzer._linear_regression_slope(flat)
    assert abs(slope_flat) < 0.1


def test_confidence_assessment():
    """Confidence should correlate with data stability"""
    analyzer = ResourceAnalyzer()

    stable = [50.0] * 100
    conf_stable = analyzer._assess_confidence(stable)
    assert conf_stable == "high"

    volatile = [i * 2 for i in range(100)]
    conf_volatile = analyzer._assess_confidence(volatile)
    assert conf_volatile in ["low", "medium"]
