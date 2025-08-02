"""
LeaseWatch - Automated Apartment Pricing Tracker
Clean entry point for the Python application
"""

import asyncio
from typing import List
from datetime import datetime

from src.scrapers import scrape_camden, scrape_columns, scrape_drift
from src.utils.data_processor import DataProcessor
from src.utils.report_generator import ReportGenerator
from src.utils.logger import Logger
from src.types.types import FloorPlan, ScrapingResult
from src.services.storage import default_storage
from src.services.report import default_report_service

# Create a quieter logger for main app
logger = Logger("LeaseWatch", quiet=False)


async def scrape_property(scraper_func, property_name: str) -> tuple[List[FloorPlan], ScrapingResult]:
    """Scrape a single property with error handling"""
    try:
        print(f"🏢 Scraping {property_name}...", end=" ", flush=True)
        floor_plans = await scraper_func()
        print(f"✅ {len(floor_plans)} units found")
        
        return floor_plans, ScrapingResult(
            success=True,
            message=f'{property_name} scraping completed successfully',
            timestamp=DataProcessor.format_timestamp(),
            source=property_name,
            floor_plans=floor_plans,
            errors=[]
        )
    except Exception as error:
        error_msg = str(error)
        print(f"❌ Failed: {error_msg}")
        
        return [], ScrapingResult(
            success=False,
            message=f'{property_name} scraping failed: {error_msg}',
            timestamp=DataProcessor.format_timestamp(),
            source=property_name,
            floor_plans=[],
            errors=[error_msg]
        )


async def main() -> None:
    """Main function to run the apartment pricing tracker"""
    try:
        print('🏡 LeaseWatch - Apartment Pricing Tracker')
        print(f'📅 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print()
        
        all_floor_plans: List[FloorPlan] = []
        scraping_results: List[ScrapingResult] = []
        
        # Run scrapers
        properties = [
            (scrape_camden, "Camden Dunwoody"),
            (scrape_columns, "The Columns at Lake Ridge"),
            (scrape_drift, "Drift Dunwoody")
        ]
        
        for scraper_func, property_name in properties:
            floor_plans, result = await scrape_property(scraper_func, property_name)
            all_floor_plans.extend(floor_plans)
            scraping_results.append(result)
        
        print()
        
        # Validate data
        valid_floor_plans = []
        for fp in all_floor_plans:
            if DataProcessor.validate_floor_plan(fp.model_dump()):
                valid_floor_plans.append(fp)
        
        if len(valid_floor_plans) != len(all_floor_plans):
            print(f"⚠️  Filtered out {len(all_floor_plans) - len(valid_floor_plans)} invalid floor plans")
        
        if not valid_floor_plans:
            print("❌ No valid floor plans found")
            return
        
        # Generate and save reports
        print("📊 Generating reports...")
        daily_report = default_report_service.generate_daily_report(valid_floor_plans, scraping_results)
        default_storage.save_daily_data(valid_floor_plans, daily_report)
        
        # Display summary
        print()
        print("📋 SUMMARY")
        print("=" * 40)
        print(f"📊 Total Units Found: {len(valid_floor_plans)}")
        
        # Group by property
        properties_data = {}
        for fp in valid_floor_plans:
            if fp.property_name not in properties_data:
                properties_data[fp.property_name] = []
            properties_data[fp.property_name].append(fp)
        
        for prop_name, prop_plans in properties_data.items():
            prices = [fp.price for fp in prop_plans if fp.price > 0]
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                print(f"🏢 {prop_name}: {len(prop_plans)} units")
                print(f"   💰 ${min_price:,.0f} - ${max_price:,.0f} (avg: ${avg_price:,.0f})")
        
        print()
        
        # Overall stats
        all_prices = [fp.price for fp in valid_floor_plans if fp.price > 0]
        if all_prices:
            print(f"💰 Overall Price Range: ${min(all_prices):,.0f} - ${max(all_prices):,.0f}")
            print(f"💵 Average Price: ${sum(all_prices)/len(all_prices):,.0f}")
        
        # Success rate
        successful_scrapes = len([sr for sr in scraping_results if sr.success])
        print(f"✅ Success Rate: {successful_scrapes}/{len(scraping_results)} properties")
        
        print()
        print("✅ Data saved to ./data/ directory")
        print("🌐 Start HTTP server with: python server.py")
        
    except Exception as error:
        print(f'❌ Fatal error: {str(error)}')
        raise


if __name__ == '__main__':
    asyncio.run(main())
