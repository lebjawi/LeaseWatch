"""
LeaseWatch - Automated Apartment Pricing Tracker
Entry point for the Python application
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

logger = Logger("LeaseWatch")


async def main() -> None:
    """Main function to run the apartment pricing tracker"""
    try:
        logger.info('🏡 LeaseWatch - Starting apartment pricing tracker...')
        logger.info(f'📅 Date: {datetime.now().isoformat()}')
        
        all_floor_plans: List[FloorPlan] = []
        scraping_results: List[ScrapingResult] = []
        
        # Phase 1: Run scrapers and collect data
        logger.phase_start('Phase 1: Data Collection')
        
        # Camden scraping
        try:
            camden_plans = await scrape_camden()
            all_floor_plans.extend(camden_plans)
            scraping_results.append(ScrapingResult(
                success=True,
                message='Camden scraping completed successfully',
                timestamp=DataProcessor.format_timestamp(),
                source='Camden Dunwoody',
                floor_plans=camden_plans,
                errors=[]
            ))
            logger.success(f'Camden: {len(camden_plans)} floor plans extracted')
            
        except Exception as error:
            error_msg = str(error)
            logger.error(f'Camden scraping failed: {error_msg}')
            scraping_results.append(ScrapingResult(
                success=False,
                message=f'Camden scraping failed: {error_msg}',
                timestamp=DataProcessor.format_timestamp(),
                source='Camden Dunwoody',
                floor_plans=[],
                errors=[error_msg]
            ))
        
        # Columns scraping
        try:
            columns_plans = await scrape_columns()
            all_floor_plans.extend(columns_plans)
            scraping_results.append(ScrapingResult(
                success=True,
                message='Columns scraping completed successfully',
                timestamp=DataProcessor.format_timestamp(),
                source='The Columns at Lake Ridge',
                floor_plans=columns_plans,
                errors=[]
            ))
            logger.success(f'Columns: {len(columns_plans)} floor plans extracted')
            
        except Exception as error:
            error_msg = str(error)
            logger.error(f'Columns scraping failed: {error_msg}')
            scraping_results.append(ScrapingResult(
                success=False,
                message=f'Columns scraping failed: {error_msg}',
                timestamp=DataProcessor.format_timestamp(),
                source='The Columns at Lake Ridge',
                floor_plans=[],
                errors=[error_msg]
            ))
        
        # Drift scraping
        try:
            drift_plans = await scrape_drift()
            all_floor_plans.extend(drift_plans)
            scraping_results.append(ScrapingResult(
                success=True,
                message='Drift scraping completed successfully',
                timestamp=DataProcessor.format_timestamp(),
                source='Drift Dunwoody',
                floor_plans=drift_plans,
                errors=[]
            ))
            logger.success(f'Drift: {len(drift_plans)} floor plans extracted')
            
        except Exception as error:
            error_msg = str(error)
            logger.error(f'Drift scraping failed: {error_msg}')
            scraping_results.append(ScrapingResult(
                success=False,
                message=f'Drift scraping failed: {error_msg}',
                timestamp=DataProcessor.format_timestamp(),
                source='Drift Dunwoody',
                floor_plans=[],
                errors=[error_msg]
            ))
        
        # Phase 2: Process and validate data
        logger.phase_start('Phase 2: Data Processing & Validation')
        
        # Validate and clean floor plans
        valid_floor_plans = []
        for fp in all_floor_plans:
            if DataProcessor.validate_floor_plan(fp.model_dump()):
                valid_floor_plans.append(fp)
            else:
                logger.warning(f'❌ Removed invalid floor plan: {fp.name}')
        
        logger.info(f'✅ Data validation complete: {len(valid_floor_plans)}/{len(all_floor_plans)} floor plans valid')
        
        # Phase 3: Generate reports
        logger.phase_start('Phase 3: Report Generation')
        
        if valid_floor_plans:
            # Generate daily report
            daily_report = default_report_service.generate_daily_report(valid_floor_plans, scraping_results)
            
            # Save data
            default_storage.save_daily_data(valid_floor_plans, daily_report)
            
            # Generate and display reports
            logger.info('\n' + ReportGenerator.generate_daily_summary(valid_floor_plans))
            logger.info('\n' + default_report_service.generate_executive_summary(valid_floor_plans, scraping_results))
            
            # Generate detailed reports
            comparison_report = default_report_service.generate_property_comparison_report(valid_floor_plans)
            bedroom_analysis = default_report_service.generate_bedroom_analysis_report(valid_floor_plans)
            availability_report = default_report_service.generate_availability_report(valid_floor_plans)
            
            logger.info('\n' + comparison_report)
            logger.info('\n' + bedroom_analysis)
            logger.info('\n' + availability_report)
            
            # Best value recommendations
            logger.info('\n' + ReportGenerator.generate_comparison_report(valid_floor_plans, 1))  # 1 bedroom
            logger.info('\n' + ReportGenerator.generate_comparison_report(valid_floor_plans, 2))  # 2 bedroom
            
        else:
            logger.error('❌ No valid floor plans found. Check scraping results.')
        
        # Phase 4: Cleanup and summary
        logger.phase_start('Phase 4: Cleanup & Summary')
        
        # Cleanup old data (keep last 90 days)
        default_storage.cleanup_old_data(90)
        
        # Final summary
        successful_scrapes = len([sr for sr in scraping_results if sr.success])
        total_scrapes = len(scraping_results)
        
        logger.info('\n🎯 FINAL SUMMARY')
        logger.info('=' * 50)
        logger.info(f'📊 Total Floor Plans Found: {len(valid_floor_plans)}')
        logger.info(f'🏢 Properties Scraped: {total_scrapes}')
        logger.info(f'✅ Successful Scrapes: {successful_scrapes}/{total_scrapes}')
        logger.info(f'⏱️  Execution Time: {datetime.now().strftime("%H:%M:%S")}')
        
        if valid_floor_plans:
            properties = list(set(fp.property_name for fp in valid_floor_plans))
            for prop in properties:
                prop_count = len([fp for fp in valid_floor_plans if fp.property_name == prop])
                logger.info(f'   • {prop}: {prop_count} units')
        
        logger.success('🏡 LeaseWatch execution completed successfully!')
        
    except Exception as error:
        logger.error(f'❌ Fatal error in main execution: {str(error)}')
        raise


if __name__ == '__main__':
    asyncio.run(main())
