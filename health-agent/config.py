#!/usr/bin/env python3
"""
Configuration for Kelly's Health Correlations Agent.
"""

import os
from datetime import datetime, timedelta

# Data Collection Settings
OURA_SKILL_PATH = "/data/workspace/skills/oura"
STRAVA_SKILL_PATH = "/data/workspace/skills/strava"
DATA_STORAGE_PATH = "/data/workspace/health-agent/data"

# Vault Integration
KELLY_VAULT_PATH = "/data/kelly-vault"
HEALTH_VAULT_PATH = "/data/kelly-vault/health"
DAILY_REPORTS_PATH = "/data/kelly-vault/health/daily"
INSIGHTS_PATH = "/data/kelly-vault/health/insights"

# Analysis Parameters
MIN_DATA_POINTS = 7  # Minimum days of data for correlation analysis
CORRELATION_THRESHOLD = 0.3  # Minimum correlation strength to report
LOOKBACK_DAYS = 30  # Days to include in analysis

# Sleep Thresholds (based on Kelly's patterns)
OPTIMAL_SLEEP_MIN = 8.0  # Hours for optimal performance
MIN_SLEEP_WARNING = 6.5  # Hours below which to flag poor sleep
HRV_DECLINE_THRESHOLD = 15  # % decline to flag as significant

# Readiness Score Bands
READINESS_EXCELLENT = 85
READINESS_GOOD = 70
READINESS_FAIR = 55
# Below 55 = Poor

# Running Performance Bands (minutes per mile)
KELLY_TARGET_PACE = 8.5  # Target easy pace in min/mi
PACE_VARIATION_THRESHOLD = 0.3  # Pace change to consider significant (30 seconds)

# Reporting Settings
DAILY_BRIEF_TIME = "06:30"  # When to generate morning brief
WEEKLY_REPORT_DAY = "Sunday"  # Day to generate weekly summary
MAX_INSIGHTS_PER_BRIEF = 3  # Limit insights to avoid information overload

# Cycle Tracking (when data becomes available)
CYCLE_PHASES = {
    "menstrual": (1, 5),     # Days 1-5
    "follicular": (6, 14),   # Days 6-14  
    "ovulatory": (14, 16),   # Days 14-16
    "luteal": (17, 28)       # Days 17-28
}

class HealthConfig:
    """Dynamic configuration with data validation."""
    
    @staticmethod
    def get_data_path(filename: str = None) -> str:
        """Get path for data storage files."""
        os.makedirs(DATA_STORAGE_PATH, exist_ok=True)
        if filename:
            return os.path.join(DATA_STORAGE_PATH, filename)
        return DATA_STORAGE_PATH
    
    @staticmethod
    def get_date_range(days_back: int = LOOKBACK_DAYS) -> tuple:
        """Get date range for analysis (start_date, end_date)."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        return start_date, end_date
    
    @staticmethod
    def categorize_sleep_hours(hours: float) -> str:
        """Categorize sleep duration."""
        if hours >= OPTIMAL_SLEEP_MIN:
            return "optimal"
        elif hours >= MIN_SLEEP_WARNING:
            return "adequate" 
        else:
            return "poor"
    
    @staticmethod
    def categorize_readiness(score: int) -> str:
        """Categorize readiness score."""
        if score >= READINESS_EXCELLENT:
            return "excellent"
        elif score >= READINESS_GOOD:
            return "good"
        elif score >= READINESS_FAIR:
            return "fair"
        else:
            return "poor"
    
    @staticmethod
    def pace_delta_significant(pace1: float, pace2: float) -> bool:
        """Check if pace difference is significant."""
        return abs(pace1 - pace2) >= PACE_VARIATION_THRESHOLD
    
    @staticmethod
    def should_generate_brief() -> bool:
        """Check if it's time for daily brief."""
        now = datetime.now().strftime("%H:%M")
        return now == DAILY_BRIEF_TIME
    
    @staticmethod
    def should_generate_weekly_report() -> bool:
        """Check if it's time for weekly report."""
        return datetime.now().strftime("%A") == WEEKLY_REPORT_DAY
    
    @staticmethod
    def ensure_vault_paths():
        """Create necessary vault directories."""
        import os
        os.makedirs(KELLY_VAULT_PATH, exist_ok=True)
        os.makedirs(HEALTH_VAULT_PATH, exist_ok=True)
        os.makedirs(DAILY_REPORTS_PATH, exist_ok=True)
        os.makedirs(INSIGHTS_PATH, exist_ok=True)
    
    @staticmethod
    def get_vault_path(subfolder: str = "", filename: str = None) -> str:
        """Get path for vault files."""
        HealthConfig.ensure_vault_paths()
        if subfolder:
            base_path = os.path.join(HEALTH_VAULT_PATH, subfolder)
            os.makedirs(base_path, exist_ok=True)
        else:
            base_path = HEALTH_VAULT_PATH
        
        if filename:
            return os.path.join(base_path, filename)
        return base_path

if __name__ == "__main__":
    # Config validation
    print(f"Data storage: {HealthConfig.get_data_path()}")
    print(f"Analysis window: {HealthConfig.get_date_range()}")
    print(f"Sleep categories: optimal >={OPTIMAL_SLEEP_MIN}h, warning <{MIN_SLEEP_WARNING}h")
    print(f"Target pace: {KELLY_TARGET_PACE} min/mi ±{PACE_VARIATION_THRESHOLD}")