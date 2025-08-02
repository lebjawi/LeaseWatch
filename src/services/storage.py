"""
Storage Service
Handles data storage and retrieval for LeaseWatch application
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from pathlib import Path
from ..types.types import FloorPlan, DailyReport, PropertySummary, ScrapingResult
from ..utils.logger import Logger

logger = Logger("StorageService")


class StorageService:
    """
    Handles local JSON storage for apartment data
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "daily").mkdir(exist_ok=True)
        (self.data_dir / "reports").mkdir(exist_ok=True)
        (self.data_dir / "raw").mkdir(exist_ok=True)
    
    def save_daily_data(self, floor_plans: List[FloorPlan], report: DailyReport) -> str:
        """Save daily scraped floor plan data"""
        try:
            today = date.today().isoformat()
            
            # Save floor plans
            floor_plans_file = self.data_dir / "daily" / f"{today}_floor_plans.json"
            floor_plans_data = [fp.model_dump() for fp in floor_plans]
            
            with open(floor_plans_file, 'w', encoding='utf-8') as f:
                json.dump(floor_plans_data, f, indent=2, ensure_ascii=False)
            
            # Save report
            report_file = self.data_dir / "reports" / f"{today}_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved daily data: {len(floor_plans)} floor plans to {floor_plans_file}")
            logger.info(f"✅ Saved daily report to {report_file}")
            
            return today
            
        except Exception as e:
            logger.error(f"❌ Error saving daily data: {str(e)}")
            raise
    
    def load_daily_data(self, date_str: Optional[str] = None) -> List[FloorPlan]:
        """Load daily floor plan data"""
        try:
            if not date_str:
                date_str = date.today().isoformat()
            
            floor_plans_file = self.data_dir / "daily" / f"{date_str}_floor_plans.json"
            
            if not floor_plans_file.exists():
                logger.warning(f"⚠️ No data found for date: {date_str}")
                return []
            
            with open(floor_plans_file, 'r', encoding='utf-8') as f:
                floor_plans_data = json.load(f)
            
            floor_plans = [FloorPlan(**fp) for fp in floor_plans_data]
            logger.info(f"✅ Loaded {len(floor_plans)} floor plans from {date_str}")
            
            return floor_plans
            
        except Exception as e:
            logger.error(f"❌ Error loading daily data: {str(e)}")
            return []
    
    def load_daily_report(self, date_str: Optional[str] = None) -> Optional[DailyReport]:
        """Load daily report"""
        try:
            if not date_str:
                date_str = date.today().isoformat()
            
            report_file = self.data_dir / "reports" / f"{date_str}_report.json"
            
            if not report_file.exists():
                logger.warning(f"⚠️ No report found for date: {date_str}")
                return None
            
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            report = DailyReport(**report_data)
            logger.info(f"✅ Loaded daily report from {date_str}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error loading daily report: {str(e)}")
            return None
    
    def save_raw_data(self, property_name: str, raw_data: List[Dict[str, Any]]) -> str:
        """Save raw scraped data for debugging"""
        try:
            timestamp = datetime.now().isoformat().replace(':', '-')
            filename = f"{timestamp}_{property_name.lower().replace(' ', '_')}_raw.json"
            raw_file = self.data_dir / "raw" / filename
            
            with open(raw_file, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"✅ Saved raw data for {property_name}: {raw_file}")
            return str(raw_file)
            
        except Exception as e:
            logger.error(f"❌ Error saving raw data: {str(e)}")
            raise
    
    def get_available_dates(self) -> List[str]:
        """Get list of available data dates"""
        try:
            daily_dir = self.data_dir / "daily"
            dates = []
            
            for file in daily_dir.glob("*_floor_plans.json"):
                date_str = file.stem.replace('_floor_plans', '')
                dates.append(date_str)
            
            return sorted(dates, reverse=True)  # Most recent first
            
        except Exception as e:
            logger.error(f"❌ Error getting available dates: {str(e)}")
            return []
    
    def get_property_history(self, property_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical data for a specific property"""
        try:
            available_dates = self.get_available_dates()
            history = []
            
            for date_str in available_dates[:days]:  # Last N days
                floor_plans = self.load_daily_data(date_str)
                property_plans = [fp for fp in floor_plans if fp.property_name == property_name]
                
                if property_plans:
                    avg_price = sum(fp.price for fp in property_plans) / len(property_plans)
                    avg_sqft_price = sum(fp.price_per_sq_ft for fp in property_plans) / len(property_plans)
                    
                    history.append({
                        'date': date_str,
                        'property_name': property_name,
                        'unit_count': len(property_plans),
                        'avg_price': round(avg_price, 2),
                        'avg_price_per_sqft': round(avg_sqft_price, 2),
                        'min_price': min(fp.price for fp in property_plans),
                        'max_price': max(fp.price for fp in property_plans)
                    })
            
            logger.info(f"✅ Retrieved {len(history)} historical records for {property_name}")
            return history
            
        except Exception as e:
            logger.error(f"❌ Error getting property history: {str(e)}")
            return []
    
    def cleanup_old_data(self, keep_days: int = 90):
        """Clean up data older than specified days"""
        try:
            cutoff_date = datetime.now().date() - timedelta(days=keep_days)
            cutoff_str = cutoff_date.isoformat()
            
            deleted_count = 0
            
            # Clean daily data
            for file in (self.data_dir / "daily").glob("*.json"):
                date_str = file.stem.split('_')[0]
                if date_str < cutoff_str:
                    file.unlink()
                    deleted_count += 1
            
            # Clean reports
            for file in (self.data_dir / "reports").glob("*.json"):
                date_str = file.stem.split('_')[0]
                if date_str < cutoff_str:
                    file.unlink()
                    deleted_count += 1
            
            # Clean raw data (keep less - only 30 days)
            raw_cutoff = datetime.now().date() - timedelta(days=30)
            raw_cutoff_str = raw_cutoff.isoformat()
            
            for file in (self.data_dir / "raw").glob("*.json"):
                # Extract date from timestamp filename
                try:
                    timestamp = file.stem.split('_')[0]
                    file_date = datetime.fromisoformat(timestamp.replace('-', ':')).date()
                    if file_date < raw_cutoff:
                        file.unlink()
                        deleted_count += 1
                except Exception:
                    # If we can't parse the date, skip it
                    continue
            
            logger.info(f"✅ Cleaned up {deleted_count} old data files")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {str(e)}")
    
    def export_data(self, start_date: str, end_date: str, output_file: str):
        """Export data for a date range to a single file"""
        try:
            all_data = []
            current_date = datetime.fromisoformat(start_date).date()
            end_date_obj = datetime.fromisoformat(end_date).date()
            
            while current_date <= end_date_obj:
                date_str = current_date.isoformat()
                floor_plans = self.load_daily_data(date_str)
                
                if floor_plans:
                    daily_data = {
                        'date': date_str,
                        'floor_plans': [fp.model_dump() for fp in floor_plans]
                    }
                    all_data.append(daily_data)
                
                current_date += timedelta(days=1)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exported data from {start_date} to {end_date}: {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting data: {str(e)}")
            raise


# Create default storage service instance
default_storage = StorageService()
