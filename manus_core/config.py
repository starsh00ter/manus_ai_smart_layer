#!/usr/bin/env python3

"""
Unified Configuration Module for Manus AI Projects

Provides centralized configuration management with environment variable support,
validation, and dynamic updates.
"""

import os
import json
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class CreditConfig:
    """Credit management configuration"""
    daily_limit: int = 300000
    warning_threshold: float = 0.8
    max_single_operation: int = 50000
    emergency_threshold: float = 0.95
    refund_window_hours: int = 24
    auto_reset_enabled: bool = True
    
    def __post_init__(self):
        """Validate credit configuration"""
        if self.daily_limit <= 0:
            raise ValueError("Daily limit must be positive")
        if not 0 <= self.warning_threshold <= 1:
            raise ValueError("Warning threshold must be between 0 and 1")
        if not 0 <= self.emergency_threshold <= 1:
            raise ValueError("Emergency threshold must be between 0 and 1")
        if self.warning_threshold >= self.emergency_threshold:
            raise ValueError("Warning threshold must be less than emergency threshold")

@dataclass
class SystemConfig:
    """System-wide configuration"""
    session_timeout: int = 3600
    reflection_interval: int = 14400  # 4 hours
    max_trajectory_length: int = 1000
    cache_ttl: int = 86400  # 24 hours
    cleanup_interval: int = 86400  # 24 hours
    max_concurrent_operations: int = 10
    operation_timeout: int = 300  # 5 minutes
    
    def __post_init__(self):
        """Validate system configuration"""
        if self.session_timeout <= 0:
            raise ValueError("Session timeout must be positive")
        if self.reflection_interval <= 0:
            raise ValueError("Reflection interval must be positive")
        if self.max_trajectory_length <= 0:
            raise ValueError("Max trajectory length must be positive")

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: Optional[str] = None
    key: Optional[str] = None
    connection_timeout: int = 30
    query_timeout: int = 60
    max_connections: int = 20
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        """Validate database configuration"""
        if self.connection_timeout <= 0:
            raise ValueError("Connection timeout must be positive")
        if self.query_timeout <= 0:
            raise ValueError("Query timeout must be positive")

@dataclass
class APIConfig:
    """API configuration"""
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"
    manus_api_key: Optional[str] = None
    manus_base_url: str = "https://api.manus.ai"
    request_timeout: int = 30
    max_retries: int = 3
    rate_limit_per_minute: int = 60
    
    def __post_init__(self):
        """Validate API configuration"""
        if self.request_timeout <= 0:
            raise ValueError("Request timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")

@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling functionality"""
    credit_budget_required: bool = True
    auto_reflection: bool = True
    schema_validation: bool = True
    self_optimization: bool = True
    audit_logging: bool = True
    performance_monitoring: bool = True
    cache_enabled: bool = True
    debug_mode: bool = False

class Config:
    """Unified configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None, load_env: bool = True):
        self.config_file = config_file
        self._config_cache = {}
        
        # Initialize configurations
        self.credit = CreditConfig()
        self.system = SystemConfig()
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.features = FeatureFlags()
        
        # Load configurations
        if load_env:
            self._load_from_environment()
        
        if config_file and Path(config_file).exists():
            self._load_from_file(config_file)
        
        # Validate final configuration
        self._validate_configuration()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        
        # Credit configuration
        self.credit.daily_limit = int(os.getenv("DAILY_CREDIT_LIMIT", str(self.credit.daily_limit)))
        self.credit.warning_threshold = float(os.getenv("CREDIT_WARNING_THRESHOLD", str(self.credit.warning_threshold)))
        self.credit.max_single_operation = int(os.getenv("MAX_SINGLE_OPERATION", str(self.credit.max_single_operation)))
        self.credit.emergency_threshold = float(os.getenv("CREDIT_EMERGENCY_THRESHOLD", str(self.credit.emergency_threshold)))
        self.credit.refund_window_hours = int(os.getenv("REFUND_WINDOW_HOURS", str(self.credit.refund_window_hours)))
        self.credit.auto_reset_enabled = os.getenv("AUTO_RESET_ENABLED", "true").lower() == "true"
        
        # System configuration
        self.system.session_timeout = int(os.getenv("SESSION_TIMEOUT", str(self.system.session_timeout)))
        self.system.reflection_interval = int(os.getenv("REFLECTION_INTERVAL", str(self.system.reflection_interval)))
        self.system.max_trajectory_length = int(os.getenv("MAX_TRAJECTORY_LENGTH", str(self.system.max_trajectory_length)))
        self.system.cache_ttl = int(os.getenv("CACHE_TTL", str(self.system.cache_ttl)))
        self.system.cleanup_interval = int(os.getenv("CLEANUP_INTERVAL", str(self.system.cleanup_interval)))
        self.system.max_concurrent_operations = int(os.getenv("MAX_CONCURRENT_OPERATIONS", str(self.system.max_concurrent_operations)))
        self.system.operation_timeout = int(os.getenv("OPERATION_TIMEOUT", str(self.system.operation_timeout)))
        
        # Database configuration
        self.database.url = os.getenv("SUPABASE_URL")
        self.database.key = os.getenv("SUPABASE_KEY")
        self.database.connection_timeout = int(os.getenv("DB_CONNECTION_TIMEOUT", str(self.database.connection_timeout)))
        self.database.query_timeout = int(os.getenv("DB_QUERY_TIMEOUT", str(self.database.query_timeout)))
        self.database.max_connections = int(os.getenv("DB_MAX_CONNECTIONS", str(self.database.max_connections)))
        self.database.retry_attempts = int(os.getenv("DB_RETRY_ATTEMPTS", str(self.database.retry_attempts)))
        self.database.retry_delay = float(os.getenv("DB_RETRY_DELAY", str(self.database.retry_delay)))
        
        # API configuration
        self.api.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", self.api.deepseek_base_url)
        self.api.manus_api_key = os.getenv("MANUS_API_KEY")
        self.api.manus_base_url = os.getenv("MANUS_BASE_URL", self.api.manus_base_url)
        self.api.request_timeout = int(os.getenv("API_REQUEST_TIMEOUT", str(self.api.request_timeout)))
        self.api.max_retries = int(os.getenv("API_MAX_RETRIES", str(self.api.max_retries)))
        self.api.rate_limit_per_minute = int(os.getenv("API_RATE_LIMIT", str(self.api.rate_limit_per_minute)))
        
        # Feature flags
        self.features.credit_budget_required = os.getenv("CREDIT_BUDGET_REQUIRED", "true").lower() == "true"
        self.features.auto_reflection = os.getenv("AUTO_REFLECTION", "true").lower() == "true"
        self.features.schema_validation = os.getenv("SCHEMA_VALIDATION", "true").lower() == "true"
        self.features.self_optimization = os.getenv("SELF_OPTIMIZATION", "true").lower() == "true"
        self.features.audit_logging = os.getenv("AUDIT_LOGGING", "true").lower() == "true"
        self.features.performance_monitoring = os.getenv("PERFORMANCE_MONITORING", "true").lower() == "true"
        self.features.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.features.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    def _load_from_file(self, config_file: str):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            
            # Update configurations from file
            if "credit" in file_config:
                for key, value in file_config["credit"].items():
                    if hasattr(self.credit, key):
                        setattr(self.credit, key, value)
            
            if "system" in file_config:
                for key, value in file_config["system"].items():
                    if hasattr(self.system, key):
                        setattr(self.system, key, value)
            
            if "database" in file_config:
                for key, value in file_config["database"].items():
                    if hasattr(self.database, key):
                        setattr(self.database, key, value)
            
            if "api" in file_config:
                for key, value in file_config["api"].items():
                    if hasattr(self.api, key):
                        setattr(self.api, key, value)
            
            if "features" in file_config:
                for key, value in file_config["features"].items():
                    if hasattr(self.features, key):
                        setattr(self.features, key, value)
                        
        except Exception as e:
            print(f"⚠️ Error loading config file {config_file}: {e}")
    
    def _validate_configuration(self):
        """Validate the complete configuration"""
        try:
            # Re-run post_init validation for all configs
            self.credit.__post_init__()
            self.system.__post_init__()
            self.database.__post_init__()
            self.api.__post_init__()
            
        except ValueError as e:
            raise ValueError(f"Configuration validation failed: {e}")
    
    def save_to_file(self, config_file: str):
        """Save current configuration to file"""
        config_dict = {
            "credit": asdict(self.credit),
            "system": asdict(self.system),
            "database": asdict(self.database),
            "api": asdict(self.api),
            "features": asdict(self.features)
        }
        
        # Remove sensitive information
        if "key" in config_dict["database"]:
            config_dict["database"]["key"] = "***REDACTED***"
        if "deepseek_api_key" in config_dict["api"]:
            config_dict["api"]["deepseek_api_key"] = "***REDACTED***"
        if "manus_api_key" in config_dict["api"]:
            config_dict["api"]["manus_api_key"] = "***REDACTED***"
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            "credit": {
                "daily_limit": self.credit.daily_limit,
                "warning_threshold": self.credit.warning_threshold,
                "emergency_threshold": self.credit.emergency_threshold,
                "auto_reset_enabled": self.credit.auto_reset_enabled
            },
            "system": {
                "session_timeout": self.system.session_timeout,
                "reflection_interval": self.system.reflection_interval,
                "max_trajectory_length": self.system.max_trajectory_length,
                "cache_ttl": self.system.cache_ttl
            },
            "database": {
                "url_configured": bool(self.database.url),
                "key_configured": bool(self.database.key),
                "connection_timeout": self.database.connection_timeout,
                "max_connections": self.database.max_connections
            },
            "api": {
                "deepseek_configured": bool(self.api.deepseek_api_key),
                "manus_configured": bool(self.api.manus_api_key),
                "request_timeout": self.api.request_timeout,
                "rate_limit": self.api.rate_limit_per_minute
            },
            "features": asdict(self.features)
        }
    
    def update_config(self, section: str, key: str, value: Any):
        """Update a specific configuration value"""
        if section == "credit" and hasattr(self.credit, key):
            setattr(self.credit, key, value)
            self.credit.__post_init__()  # Validate
        elif section == "system" and hasattr(self.system, key):
            setattr(self.system, key, value)
            self.system.__post_init__()  # Validate
        elif section == "database" and hasattr(self.database, key):
            setattr(self.database, key, value)
            self.database.__post_init__()  # Validate
        elif section == "api" and hasattr(self.api, key):
            setattr(self.api, key, value)
            self.api.__post_init__()  # Validate
        elif section == "features" and hasattr(self.features, key):
            setattr(self.features, key, value)
        else:
            raise ValueError(f"Unknown configuration section.key: {section}.{key}")
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        return getattr(self.features, feature_name, False)
    
    def get_credit_status(self) -> Dict[str, Any]:
        """Get credit configuration status"""
        return {
            "daily_limit": self.credit.daily_limit,
            "warning_threshold": self.credit.warning_threshold,
            "emergency_threshold": self.credit.emergency_threshold,
            "max_single_operation": self.credit.max_single_operation,
            "warning_tokens": int(self.credit.daily_limit * self.credit.warning_threshold),
            "emergency_tokens": int(self.credit.daily_limit * self.credit.emergency_threshold),
            "auto_reset_enabled": self.credit.auto_reset_enabled
        }
    
    def validate_operation_cost(self, estimated_tokens: int) -> Dict[str, Any]:
        """Validate if an operation cost is within limits"""
        if estimated_tokens > self.credit.max_single_operation:
            return {
                "valid": False,
                "reason": f"Operation cost {estimated_tokens} exceeds maximum {self.credit.max_single_operation}",
                "max_allowed": self.credit.max_single_operation
            }
        
        return {
            "valid": True,
            "estimated_tokens": estimated_tokens,
            "max_allowed": self.credit.max_single_operation
        }

# Global configuration instance
config = Config()

# Convenience functions
def get_config() -> Config:
    """Get the global configuration instance"""
    return config

def reload_config(config_file: Optional[str] = None):
    """Reload configuration from environment and file"""
    global config
    config = Config(config_file=config_file, load_env=True)

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return config.is_feature_enabled(feature_name)

def get_credit_limit() -> int:
    """Get the daily credit limit"""
    return config.credit.daily_limit

def get_warning_threshold() -> float:
    """Get the credit warning threshold"""
    return config.credit.warning_threshold

def get_emergency_threshold() -> float:
    """Get the credit emergency threshold"""
    return config.credit.emergency_threshold

if __name__ == "__main__":
    # Test configuration
    print("🔧 Testing Configuration Module...")
    
    # Print configuration summary
    summary = config.get_config_summary()
    print(f"Configuration loaded:")
    print(f"  Credit limit: {summary['credit']['daily_limit']}")
    print(f"  Database configured: {summary['database']['url_configured']}")
    print(f"  DeepSeek configured: {summary['api']['deepseek_configured']}")
    print(f"  Features enabled: {sum(summary['features'].values())}/{len(summary['features'])}")
    
    # Test validation
    try:
        config.update_config("credit", "daily_limit", 500000)
        print("✅ Configuration update successful")
    except Exception as e:
        print(f"❌ Configuration update failed: {e}")
    
    # Test feature check
    print(f"Auto reflection enabled: {is_feature_enabled('auto_reflection')}")
    print(f"Debug mode enabled: {is_feature_enabled('debug_mode')}")
    
    print("✅ Configuration module test complete")

