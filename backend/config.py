"""
Configuration management for Task Mining Multi-Agent System
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Data Sources Configuration
    # Use relative path from the config file location
    _config_dir = Path(__file__).parent.parent
    DATA_BASE_DIR = os.getenv(
        'DATA_BASE_DIR', 
        str(_config_dir / "Data Sources")
    )
    
    SALESFORCE_CSV_FILE = os.getenv('SALESFORCE_CSV_FILE', 'SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv')
    AMADEUS_CSV_FILE = os.getenv('AMADEUS_CSV_FILE', 'amadeus-demo-full-no-fields.csv')
    CHARTS_OUTPUT_DIR = os.getenv('CHARTS_OUTPUT_DIR', 'charts')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # API Configuration
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # Chart & Visualization Configuration
    CHART_WIDTH = int(os.getenv('CHART_WIDTH', 800))
    CHART_HEIGHT = int(os.getenv('CHART_HEIGHT', 500))
    CHART_DPI = int(os.getenv('CHART_DPI', 300))
    
    # PDF Export Configuration
    PDF_PAGE_SIZE = os.getenv('PDF_PAGE_SIZE', 'A4')
    PDF_MARGIN = int(os.getenv('PDF_MARGIN', 72))  # 1 inch in points
    PDF_TITLE_FONT_SIZE = int(os.getenv('PDF_TITLE_FONT_SIZE', 18))
    PDF_HEADING_FONT_SIZE = int(os.getenv('PDF_HEADING_FONT_SIZE', 14))
    PDF_BODY_FONT_SIZE = int(os.getenv('PDF_BODY_FONT_SIZE', 12))
    
    # Matplotlib Configuration
    MATPLOTLIB_BACKEND = os.getenv('MATPLOTLIB_BACKEND', 'Agg')
    
    # Analysis Configuration
    DEFAULT_CHART_LIMIT = int(os.getenv('DEFAULT_CHART_LIMIT', 20))
    BOTTLENECK_THRESHOLD_PERCENTILE = int(os.getenv('BOTTLENECK_THRESHOLD_PERCENTILE', 80))
    MIN_TASKS_FOR_EFFICIENCY_ANALYSIS = int(os.getenv('MIN_TASKS_FOR_EFFICIENCY_ANALYSIS', 5))
    
    # Time Analysis Configuration
    TIME_ANALYSIS_HOURS = os.getenv('TIME_ANALYSIS_HOURS', 'True').lower() == 'true'
    TIME_ANALYSIS_DAYS = os.getenv('TIME_ANALYSIS_DAYS', 'True').lower() == 'true'
    PEAK_HOURS_THRESHOLD = float(os.getenv('PEAK_HOURS_THRESHOLD', 2.0))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/task_mining.log')
    ERROR_LOG_FILE = os.getenv('ERROR_LOG_FILE', 'logs/error.log')
    CONSOLE_LOGGING = os.getenv('CONSOLE_LOGGING', 'True').lower() == 'true'
    LOG_DIR = os.getenv('LOG_DIR', './logs')
    
    # KPI Instrumentation Configuration
    ENABLE_TRACING = os.getenv('ENABLE_TRACING', 'True').lower() == 'true'
    TOLERANCE_PCT = float(os.getenv('TOLERANCE_PCT', '0.02'))  # 2% tolerance for metric verification
    
    # Security & Performance
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv('RATE_LIMIT_REQUESTS_PER_MINUTE', 60))
    
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'False').lower() == 'true'
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Development & Testing
    USE_TEST_DATA = os.getenv('USE_TEST_DATA', 'False').lower() == 'true'
    TEST_DATA_SIZE = int(os.getenv('TEST_DATA_SIZE', 1000))
    
    ENABLE_DEBUG_TOOLBAR = os.getenv('ENABLE_DEBUG_TOOLBAR', 'False').lower() == 'true'
    ENABLE_PROFILER = os.getenv('ENABLE_PROFILER', 'False').lower() == 'true'
    
    MOCK_EXTERNAL_SERVICES = os.getenv('MOCK_EXTERNAL_SERVICES', 'True').lower() == 'true'
    
    # Export & Reporting
    DEFAULT_EXPORT_FORMAT = os.getenv('DEFAULT_EXPORT_FORMAT', 'pdf')
    INCLUDE_CHART_DATA_IN_PDF = os.getenv('INCLUDE_CHART_DATA_IN_PDF', 'True').lower() == 'true'
    PDF_COMPRESSION = os.getenv('PDF_COMPRESSION', 'True').lower() == 'true'
    
    EXPORT_FILE_PREFIX = os.getenv('EXPORT_FILE_PREFIX', 'task_mining_analysis')
    EXPORT_TIMESTAMP_FORMAT = os.getenv('EXPORT_TIMESTAMP_FORMAT', '%Y%m%d_%H%M%S')
    
    # Computed properties
    @property
    def SALESFORCE_PATH(self):
        return os.path.join(self.DATA_BASE_DIR, self.SALESFORCE_CSV_FILE)
    
    @property
    def AMADEUS_PATH(self):
        return os.path.join(self.DATA_BASE_DIR, self.AMADEUS_CSV_FILE)
    
    @property
    def CHARTS_DIR(self):
        return os.path.join(self.DATA_BASE_DIR, self.CHARTS_OUTPUT_DIR)
    
    @property
    def TRACES_DIR(self):
        traces_dir = Path(self.LOG_DIR) / 'traces'
        traces_dir.mkdir(parents=True, exist_ok=True)
        return str(traces_dir)
    
    @property
    def KPIS_DIR(self):
        kpis_dir = Path(self.LOG_DIR) / 'kpis'
        kpis_dir.mkdir(parents=True, exist_ok=True)
        return str(kpis_dir)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override sensitive settings for production
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    FLASK_DEBUG = False
    CONSOLE_LOGGING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    USE_TEST_DATA = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])
