"""
Logger utility
Provides structured logging for the LeaseWatch application
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


class Logger:
    """
    Centralized logger for LeaseWatch application
    """
    
    def __init__(self, name: str = "LeaseWatch", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers(log_file)
    
    def _setup_handlers(self, log_file: Optional[str] = None):
        """Setup console and file handlers"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def success(self, message: str):
        """Log success message (using info level)"""
        self.logger.info(f"✅ {message}")
    
    def scraping_start(self, property_name: str):
        """Log start of scraping for a property"""
        self.logger.info(f"🏢 Starting scrape for {property_name}...")
    
    def scraping_complete(self, property_name: str, count: int):
        """Log completion of scraping for a property"""
        self.logger.info(f"✅ {property_name} scraping completed: {count} floor plans found")
    
    def scraping_error(self, property_name: str, error: str):
        """Log scraping error for a property"""
        self.logger.error(f"❌ {property_name} scraping failed: {error}")
    
    def phase_start(self, phase_name: str):
        """Log start of a processing phase"""
        self.logger.info(f"\n🔍 {phase_name}")
        self.logger.info("=" * 50)
    
    def browser_launch(self, property_name: str):
        """Log browser launch"""
        self.logger.info(f"🚀 Launching {property_name} browser...")
    
    def page_navigation(self, url: str):
        """Log page navigation"""
        self.logger.info(f"📍 Navigating to {url}")
    
    def page_loaded(self, title: str):
        """Log successful page load"""
        self.logger.info(f"✅ Page loaded successfully! Title: \"{title}\"")
    
    def data_extraction(self):
        """Log start of data extraction"""
        self.logger.info("🔍 Extracting floor plan data...")
    
    def browser_close(self, property_name: str):
        """Log browser closure"""
        self.logger.info(f"🔒 {property_name} browser closed")


# Create default logger instance
default_logger = Logger()

# Convenience functions for quick access
def info(message: str):
    default_logger.info(message)

def error(message: str):
    default_logger.error(message)

def debug(message: str):
    default_logger.debug(message)

def warning(message: str):
    default_logger.warning(message)

def success(message: str):
    default_logger.success(message)
