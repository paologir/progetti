"""
Configuration management for Clienti CRM
Handles loading and accessing configuration from config.toml file with environment variable overrides
"""
import os
import toml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    path: str
    echo: bool
    timeout: int

@dataclass
class ServerConfig:
    host: str
    port: int
    debug: bool
    static_dir: str
    templates_dir: str

@dataclass
class BackupConfig:
    auto_enabled: bool
    auto_interval_hours: int
    directory: str
    max_backups: int
    compress: bool

@dataclass
class ExportConfig:
    obsidian_default_path: str
    include_completed_todos: bool
    templates_dir: str

@dataclass
class BusinessConfig:
    default_hourly_rate: float
    rivalsa_percentage: float
    currency: str
    currency_symbol: str

@dataclass
class TimeTrackingConfig:
    auto_pause_minutes: int
    round_minutes: int
    auto_save_minutes: int

@dataclass
class NotificationsConfig:
    todo_warning_days: int
    billing_warning_days: int
    desktop_enabled: bool

@dataclass
class LoggingConfig:
    level: str
    file: str
    max_file_size_mb: int
    backup_count: int
    web_enabled: bool
    timer_enabled: bool

@dataclass
class CLIConfig:
    colors_enabled: bool
    progress_bars: bool
    interactive_confirmations: bool
    pagination_size: int

@dataclass
class SecurityConfig:
    audit_enabled: bool
    encrypted_backups: bool
    web_session_timeout: int

@dataclass
class IntegrationsConfig:
    calendar_enabled: bool
    email_enabled: bool

class Config:
    """Central configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config_data = {}
        self.load()
    
    def _get_default_config_path(self) -> str:
        """Get default config file path"""
        # Look for config.toml in the project root
        current_dir = Path(__file__).parent.parent
        return str(current_dir / "config.toml")
    
    def load(self):
        """Load configuration from TOML file with environment variable overrides"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_data = toml.load(f)
            else:
                print(f"⚠️ Config file not found: {self.config_path}, using defaults")
                self._config_data = {}
        except Exception as e:
            print(f"❌ Error loading config: {e}, using defaults")
            self._config_data = {}
        
        # Apply environment variable overrides
        self._apply_env_overrides()
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides following pattern: CLIENTI_SECTION_KEY"""
        for env_key, env_value in os.environ.items():
            if env_key.startswith('CLIENTI_'):
                # Convert CLIENTI_DATABASE_PATH to ['database', 'path']
                parts = env_key[8:].lower().split('_', 1)  # Remove CLIENTI_ prefix
                if len(parts) == 2:
                    section, key = parts
                    if section not in self._config_data:
                        self._config_data[section] = {}
                    
                    # Convert string values to appropriate types
                    converted_value = self._convert_env_value(env_value)
                    self._config_data[section][key] = converted_value
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Handle boolean values
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        
        # Handle numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with default fallback"""
        return self._config_data.get(section, {}).get(key, default)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self._config_data.get(section, {})
    
    # Typed configuration accessors
    @property
    def app(self) -> Dict[str, str]:
        return self.get_section('app')
    
    @property
    def database(self) -> DatabaseConfig:
        section = self.get_section('database')
        return DatabaseConfig(
            path=section.get('path', 'database.db'),
            echo=section.get('echo', False),
            timeout=section.get('timeout', 30)
        )
    
    @property
    def server(self) -> ServerConfig:
        section = self.get_section('server')
        return ServerConfig(
            host=section.get('host', '127.0.0.1'),
            port=section.get('port', 8080),
            debug=section.get('debug', False),
            static_dir=section.get('static_dir', 'web'),
            templates_dir=section.get('templates_dir', 'web/templates')
        )
    
    @property
    def backup(self) -> BackupConfig:
        section = self.get_section('backup')
        return BackupConfig(
            auto_enabled=section.get('auto_enabled', True),
            auto_interval_hours=section.get('auto_interval_hours', 24),
            directory=section.get('directory', 'data/backups'),
            max_backups=section.get('max_backups', 30),
            compress=section.get('compress', True)
        )
    
    @property
    def export(self) -> ExportConfig:
        section = self.get_section('export')
        return ExportConfig(
            obsidian_default_path=section.get('obsidian_default_path', ''),
            include_completed_todos=section.get('include_completed_todos', False),
            templates_dir=section.get('templates_dir', 'templates/obsidian')
        )
    
    @property
    def business(self) -> BusinessConfig:
        section = self.get_section('business')
        return BusinessConfig(
            default_hourly_rate=section.get('default_hourly_rate', 50.0),
            rivalsa_percentage=section.get('rivalsa_percentage', 4.0),
            currency=section.get('currency', 'EUR'),
            currency_symbol=section.get('currency_symbol', '€')
        )
    
    @property
    def time_tracking(self) -> TimeTrackingConfig:
        section = self.get_section('time_tracking')
        return TimeTrackingConfig(
            auto_pause_minutes=section.get('auto_pause_minutes', 30),
            round_minutes=section.get('round_minutes', 5),
            auto_save_minutes=section.get('auto_save_minutes', 5)
        )
    
    @property
    def notifications(self) -> NotificationsConfig:
        section = self.get_section('notifications')
        return NotificationsConfig(
            todo_warning_days=section.get('todo_warning_days', 3),
            billing_warning_days=section.get('billing_warning_days', 7),
            desktop_enabled=section.get('desktop_enabled', False)
        )
    
    @property
    def logging(self) -> LoggingConfig:
        section = self.get_section('logging')
        return LoggingConfig(
            level=section.get('level', 'INFO'),
            file=section.get('file', 'logs/clienti.log'),
            max_file_size_mb=section.get('max_file_size_mb', 10),
            backup_count=section.get('backup_count', 5),
            web_enabled=section.get('web_enabled', True),
            timer_enabled=section.get('timer_enabled', True)
        )
    
    @property
    def cli(self) -> CLIConfig:
        section = self.get_section('cli')
        return CLIConfig(
            colors_enabled=section.get('colors_enabled', True),
            progress_bars=section.get('progress_bars', True),
            interactive_confirmations=section.get('interactive_confirmations', True),
            pagination_size=section.get('pagination_size', 20)
        )
    
    @property
    def security(self) -> SecurityConfig:
        section = self.get_section('security')
        return SecurityConfig(
            audit_enabled=section.get('audit_enabled', True),
            encrypted_backups=section.get('encrypted_backups', False),
            web_session_timeout=section.get('web_session_timeout', 60)
        )
    
    @property
    def integrations(self) -> IntegrationsConfig:
        section = self.get_section('integrations')
        return IntegrationsConfig(
            calendar_enabled=section.get('calendar_enabled', False),
            email_enabled=section.get('email_enabled', False)
        )

# Global configuration instance
config = Config()

def get_config() -> Config:
    """Get global configuration instance"""
    return config

def reload_config():
    """Reload configuration from file"""
    global config
    config.load()