"""
Alert rules for Network Signal Imputation monitoring.

This module defines and evaluates alert rules for the ML pipeline.
"""

import logging
from typing import Dict, Any, List, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertRule:
    """Definition of an alert rule."""
    
    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: AlertSeverity,
        message: str,
        cooldown_minutes: int = 60
    ):
        """
        Initialize alert rule.
        
        Args:
            name: Rule name
            condition: Condition function that returns True if alert should fire
            severity: Alert severity level
            message: Alert message template
            cooldown_minutes: Minimum time between alerts
        """
        self.name = name
        self.condition = condition
        self.severity = severity
        self.message = message
        self.cooldown_minutes = cooldown_minutes
        self.last_fired = None
        
    def evaluate(self, metrics: Dict[str, Any]) -> bool:
        """
        Evaluate if the rule should fire.
        
        Args:
            metrics: Current metrics to evaluate
            
        Returns:
            True if alert should fire
        """
        # Check cooldown period
        if self.last_fired:
            minutes_since_last = (
                datetime.now() - self.last_fired
            ).total_seconds() / 60
            
            if minutes_since_last < self.cooldown_minutes:
                return False
                
        # Evaluate condition
        should_fire = self.condition(metrics)
        
        if should_fire:
            self.last_fired = datetime.now()
            
        return should_fire


class AlertManager:
    """Manage and evaluate alert rules."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize alert manager.
        
        Args:
            config: Alert configuration
        """
        self.config = config
        self.rules = []
        self.alert_history = []
        self._setup_default_rules()
        
    def _setup_default_rules(self) -> None:
        """Setup default alert rules."""
        logger.info("Setting up default alert rules...")
        
        # Model performance rules
        self.add_rule(AlertRule(
            name="high_rmse",
            condition=lambda m: m.get("rmse", 0) > 0.2,
            severity=AlertSeverity.WARNING,
            message="Model RMSE {rmse:.4f} exceeded threshold of 0.2"
        ))
        
        self.add_rule(AlertRule(
            name="critical_rmse",
            condition=lambda m: m.get("rmse", 0) > 0.3,
            severity=AlertSeverity.CRITICAL,
            message="Model RMSE {rmse:.4f} critically high (threshold: 0.3)"
        ))
        
        # Data quality rules
        self.add_rule(AlertRule(
            name="high_missing_data",
            condition=lambda m: m.get("missing_percentage", 0) > 30,
            severity=AlertSeverity.WARNING,
            message="Missing data {missing_percentage:.1f}% exceeds 30% threshold"
        ))
        
        self.add_rule(AlertRule(
            name="stale_data",
            condition=lambda m: m.get("hours_since_update", 0) > 6,
            severity=AlertSeverity.WARNING,
            message="Data has not been updated for {hours_since_update:.1f} hours"
        ))
        
        # Drift detection rules
        self.add_rule(AlertRule(
            name="feature_drift",
            condition=lambda m: m.get("max_psi", 0) > 0.1,
            severity=AlertSeverity.CRITICAL,
            message="Feature drift detected: PSI {max_psi:.4f} exceeds 0.1"
        ))
        
        self.add_rule(AlertRule(
            name="performance_drift",
            condition=lambda m: abs(m.get("performance_change_pct", 0)) > 15,
            severity=AlertSeverity.WARNING,
            message="Model performance changed by {performance_change_pct:.1f}%"
        ))
        
        # Infrastructure rules
        self.add_rule(AlertRule(
            name="high_latency",
            condition=lambda m: m.get("p95_latency_ms", 0) > 500,
            severity=AlertSeverity.WARNING,
            message="P95 inference latency {p95_latency_ms:.0f}ms exceeds 500ms"
        ))
        
        self.add_rule(AlertRule(
            name="low_prediction_volume",
            condition=lambda m: m.get("predictions_per_hour", 1000) < 100,
            severity=AlertSeverity.WARNING,
            message="Prediction volume {predictions_per_hour} below expected rate"
        ))
        
    def add_rule(self, rule: AlertRule) -> None:
        """
        Add a new alert rule.
        
        Args:
            rule: Alert rule to add
        """
        self.rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
        
    def evaluate_rules(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate all rules against current metrics.
        
        Args:
            metrics: Current metrics
            
        Returns:
            List of triggered alerts
        """
        logger.info("Evaluating alert rules...")
        
        triggered_alerts = []
        
        for rule in self.rules:
            try:
                if rule.evaluate(metrics):
                    alert = {
                        "timestamp": datetime.now().isoformat(),
                        "rule_name": rule.name,
                        "severity": rule.severity.value,
                        "message": rule.message.format(**metrics),
                        "metrics": metrics
                    }
                    
                    triggered_alerts.append(alert)
                    self.alert_history.append(alert)
                    
                    logger.warning(
                        f"Alert triggered: {rule.name} - {alert['message']}"
                    )
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
                
        return triggered_alerts
        
    def send_alerts(self, alerts: List[Dict[str, Any]]) -> None:
        """
        Send alerts through configured channels.
        
        Args:
            alerts: List of alerts to send
        """
        if not alerts:
            return
            
        logger.info(f"Sending {len(alerts)} alerts...")
        
        channels = self.config.get("channels", [])
        
        for channel in channels:
            channel_type = channel.get("type")
            
            if channel_type == "email":
                self._send_email_alerts(alerts, channel)
            elif channel_type == "slack":
                self._send_slack_alerts(alerts, channel)
            elif channel_type == "pagerduty":
                self._send_pagerduty_alerts(alerts, channel)
            else:
                logger.warning(f"Unknown alert channel: {channel_type}")
                
    def _send_email_alerts(
        self,
        alerts: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> None:
        """Send alerts via email."""
        logger.info("Sending email alerts...")
        # Implement email sending logic
        pass
        
    def _send_slack_alerts(
        self,
        alerts: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> None:
        """Send alerts to Slack."""
        logger.info("Sending Slack alerts...")
        # Implement Slack webhook logic
        pass
        
    def _send_pagerduty_alerts(
        self,
        alerts: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> None:
        """Send alerts to PagerDuty."""
        logger.info("Sending PagerDuty alerts...")
        # Implement PagerDuty integration logic
        pass
        
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get summary of recent alerts.
        
        Args:
            hours: Number of hours to include in summary
            
        Returns:
            Alert summary
        """
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert["timestamp"]).timestamp() > cutoff_time
        ]
        
        summary = {
            "total_alerts": len(recent_alerts),
            "by_severity": {},
            "by_rule": {},
            "recent_alerts": recent_alerts[-10:]
        }
        
        for alert in recent_alerts:
            severity = alert["severity"]
            rule_name = alert["rule_name"]
            
            summary["by_severity"][severity] = \
                summary["by_severity"].get(severity, 0) + 1
            summary["by_rule"][rule_name] = \
                summary["by_rule"].get(rule_name, 0) + 1
                
        return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = {
        "channels": [
            {"type": "email", "recipients": ["ml-team@company.com"]},
            {"type": "slack", "webhook_url": "https://hooks.slack.com/..."}
        ]
    }
    
    manager = AlertManager(config)
    
    # Example: Evaluate rules
    metrics = {
        "rmse": 0.25,
        "mae": 0.18,
        "missing_percentage": 15.5,
        "hours_since_update": 2.5,
        "max_psi": 0.05,
        "p95_latency_ms": 450,
        "predictions_per_hour": 1200
    }
    
    alerts = manager.evaluate_rules(metrics)
    if alerts:
        manager.send_alerts(alerts)
        
    # Get summary
    summary = manager.get_alert_summary(hours=24)
    print(f"Alert summary: {summary}")
