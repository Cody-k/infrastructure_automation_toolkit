"""Tests for resource analyzer"""

import pytest
from src.monitoring import ResourceAnalyzer, ResourceTrend, Prediction


def test_resource_analyzer_initialization():
    """ResourceAnalyzer should initialize"""
    analyzer = ResourceAnalyzer()
    assert analyzer.data_dir.exists()


def test_analyze_trends():
    """Should analyze trends or return empty dict"""
    analyzer = ResourceAnalyzer()
    trends = analyzer.analyze_trends(hours=24)

    assert isinstance(trends, dict)
    if trends:
        assert "cpu" in trends or "memory" in trends or "disk" in trends
        for trend in trends.values():
            assert isinstance(trend, ResourceTrend)
            assert trend.data_points >= 0


def test_predict_resource_needs():
    """Should generate predictions or return empty dict"""
    analyzer = ResourceAnalyzer()
    predictions = analyzer.predict_resource_needs()

    assert isinstance(predictions, dict)
    if predictions:
        for pred in predictions.values():
            assert isinstance(pred, Prediction)
            assert pred.confidence in ["high", "medium", "low"]


def test_generate_recommendations():
    """Should generate actionable recommendations"""
    analyzer = ResourceAnalyzer()
    recommendations = analyzer.generate_recommendations()

    assert isinstance(recommendations, list)
    for rec in recommendations:
        assert "resource" in rec
        assert "priority" in rec
        assert rec["priority"] in ["high", "medium", "low"]
