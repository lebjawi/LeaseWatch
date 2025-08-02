"""
Report Service
Handles report generation and management for LeaseWatch application
"""

import uuid
from typing import List, Optional
from datetime import datetime, date
from ..types.types import (
    FloorPlan, 
    DailyReport, 
    PropertySummary, 
    ScrapingResult, 
    PriceRange,
    BedroomDistribution
)
from ..utils.data_processor import DataProcessor
from ..utils.report_generator import ReportGenerator
from ..utils.logger import Logger

logger = Logger("ReportService", quiet=True)


class ReportService:
    """
    Service for generating and managing various types of reports
    """
    
    @staticmethod
    def generate_daily_report(
        floor_plans: List[FloorPlan], 
        scraping_results: List[ScrapingResult]
    ) -> DailyReport:
        """Generate a comprehensive daily report"""
        try:
            logger.info("📊 Generating daily report...")
            
            # Group floor plans by property
            properties = {}
            for fp in floor_plans:
                if fp.property_name not in properties:
                    properties[fp.property_name] = []
                properties[fp.property_name].append(fp)
            
            # Generate property summaries
            property_summaries = []
            for property_name, property_plans in properties.items():
                summary = DataProcessor.generate_property_summary(property_plans)
                property_summaries.append(summary)
            
            # Calculate overall price range
            all_prices = [fp.price for fp in floor_plans if fp.price > 0]
            overall_price_range = PriceRange(
                min=min(all_prices) if all_prices else 0,
                max=max(all_prices) if all_prices else 0
            )
            
            # Create the daily report
            report = DailyReport(
                date=DataProcessor.format_date(),
                total_properties=len(properties),
                total_floor_plans=len(floor_plans),
                overall_price_range=overall_price_range,
                property_summaries=property_summaries,
                scraping_results=scraping_results,
                generation_timestamp=DataProcessor.format_timestamp(),
                report_id=str(uuid.uuid4())
            )
            
            logger.info(f"✅ Daily report generated: {report.total_floor_plans} floor plans from {report.total_properties} properties")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating daily report: {str(e)}")
            raise
    
    @staticmethod
    def generate_property_comparison_report(floor_plans: List[FloorPlan]) -> str:
        """Generate a comparison report across all properties"""
        try:
            logger.info("📊 Generating property comparison report...")
            
            if not floor_plans:
                return "❌ No floor plans available for comparison."
            
            # Group by property
            properties = {}
            for fp in floor_plans:
                if fp.property_name not in properties:
                    properties[fp.property_name] = []
                properties[fp.property_name].append(fp)
            
            # Generate comparison report
            lines = [
                "🏢 PROPERTY COMPARISON REPORT",
                "=" * 50,
                f"📅 Date: {date.today().isoformat()}",
                f"🏢 Properties: {len(properties)}",
                f"📋 Total Floor Plans: {len(floor_plans)}",
                ""
            ]
            
            # Compare by average price
            property_avg_prices = []
            for property_name, property_plans in properties.items():
                valid_prices = [fp.price for fp in property_plans if fp.price > 0]
                if valid_prices:
                    avg_price = sum(valid_prices) / len(valid_prices)
                    property_avg_prices.append((property_name, avg_price, len(property_plans)))
            
            property_avg_prices.sort(key=lambda x: x[1])  # Sort by average price
            
            lines.append("💰 Properties by Average Price:")
            for i, (prop_name, avg_price, count) in enumerate(property_avg_prices, 1):
                lines.append(f"  {i}. {prop_name}: {ReportGenerator.format_currency(avg_price)} (avg, {count} units)")
            
            lines.append("")
            
            # Compare by price per square foot
            property_sqft_prices = []
            for property_name, property_plans in properties.items():
                valid_sqft_prices = [fp.price_per_sq_ft for fp in property_plans if fp.price_per_sq_ft > 0]
                if valid_sqft_prices:
                    avg_sqft_price = sum(valid_sqft_prices) / len(valid_sqft_prices)
                    property_sqft_prices.append((property_name, avg_sqft_price))
            
            property_sqft_prices.sort(key=lambda x: x[1])  # Sort by price per sqft
            
            lines.append("📐 Properties by Price per Sq Ft:")
            for i, (prop_name, avg_sqft_price) in enumerate(property_sqft_prices, 1):
                lines.append(f"  {i}. {prop_name}: ${avg_sqft_price:.2f}/sq ft")
            
            lines.append("")
            
            # Best value for each bedroom count
            for bedroom_count in [0, 1, 2, 3]:
                bedroom_label = "Studio" if bedroom_count == 0 else f"{bedroom_count} Bedroom"
                bedroom_plans = [fp for fp in floor_plans if fp.bedrooms == bedroom_count]
                
                if bedroom_plans:
                    best_value = min(bedroom_plans, key=lambda x: x.price_per_sq_ft if x.price_per_sq_ft > 0 else float('inf'))
                    lines.append(f"🏆 Best {bedroom_label} Value:")
                    lines.append(f"   {best_value.name} ({best_value.property_name})")
                    lines.append(f"   💰 {ReportGenerator.format_currency(best_value.price)} | ${best_value.price_per_sq_ft}/sq ft")
                    lines.append("")
            
            result = '\n'.join(lines)
            logger.info("✅ Property comparison report generated")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating property comparison report: {str(e)}")
            return f"❌ Error generating report: {str(e)}"
    
    @staticmethod
    def generate_bedroom_analysis_report(floor_plans: List[FloorPlan]) -> str:
        """Generate a detailed analysis by bedroom count"""
        try:
            logger.info("📊 Generating bedroom analysis report...")
            
            if not floor_plans:
                return "❌ No floor plans available for analysis."
            
            # Group by bedroom count
            bedroom_groups = {}
            for fp in floor_plans:
                bedroom_key = "Studio" if fp.bedrooms == 0 else f"{fp.bedrooms} Bed"
                if bedroom_key not in bedroom_groups:
                    bedroom_groups[bedroom_key] = []
                bedroom_groups[bedroom_key].append(fp)
            
            lines = [
                "🛏️ BEDROOM ANALYSIS REPORT",
                "=" * 50,
                f"📅 Date: {date.today().isoformat()}",
                f"📋 Total Floor Plans: {len(floor_plans)}",
                ""
            ]
            
            for bedroom_type, plans in sorted(bedroom_groups.items()):
                if not plans:
                    continue
                
                # Calculate statistics
                prices = [fp.price for fp in plans if fp.price > 0]
                sqft_prices = [fp.price_per_sq_ft for fp in plans if fp.price_per_sq_ft > 0]
                square_footages = [fp.square_footage for fp in plans if fp.square_footage > 0]
                
                if not prices:
                    continue
                
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                avg_sqft_price = sum(sqft_prices) / len(sqft_prices) if sqft_prices else 0
                avg_size = sum(square_footages) / len(square_footages) if square_footages else 0
                
                # Find best value
                best_value = min(plans, key=lambda x: x.price_per_sq_ft if x.price_per_sq_ft > 0 else float('inf'))
                
                lines.extend([
                    f"🏠 {bedroom_type} Units ({len(plans)} available)",
                    f"   💰 Price Range: {ReportGenerator.format_currency(min_price)} - {ReportGenerator.format_currency(max_price)}",
                    f"   💵 Average Price: {ReportGenerator.format_currency(avg_price)}",
                    f"   📐 Average Size: {ReportGenerator.format_square_footage(int(avg_size))}",
                    f"   💲 Avg Price/Sq Ft: ${avg_sqft_price:.2f}",
                    f"   🏆 Best Value: {best_value.name} ({best_value.property_name}) - ${best_value.price_per_sq_ft}/sq ft",
                    ""
                ])
            
            result = '\n'.join(lines)
            logger.info("✅ Bedroom analysis report generated")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating bedroom analysis report: {str(e)}")
            return f"❌ Error generating report: {str(e)}"
    
    @staticmethod
    def generate_availability_report(floor_plans: List[FloorPlan]) -> str:
        """Generate a report on unit availability"""
        try:
            logger.info("📊 Generating availability report...")
            
            if not floor_plans:
                return "❌ No floor plans available for availability analysis."
            
            # Group by availability status
            availability_groups = {}
            for fp in floor_plans:
                status = fp.availability
                if status not in availability_groups:
                    availability_groups[status] = []
                availability_groups[status].append(fp)
            
            # Group by property
            property_availability = {}
            for fp in floor_plans:
                prop = fp.property_name
                if prop not in property_availability:
                    property_availability[prop] = {'available': 0, 'total': 0}
                
                property_availability[prop]['total'] += 1
                if fp.availability.lower() not in ['not available', 'unavailable']:
                    property_availability[prop]['available'] += 1
            
            lines = [
                "📅 AVAILABILITY REPORT",
                "=" * 50,
                f"📅 Date: {date.today().isoformat()}",
                f"📋 Total Floor Plans: {len(floor_plans)}",
                ""
            ]
            
            # Overall availability status
            lines.append("📊 Overall Availability:")
            for status, plans in sorted(availability_groups.items()):
                percentage = (len(plans) / len(floor_plans)) * 100
                lines.append(f"   • {status}: {len(plans)} units ({percentage:.1f}%)")
            
            lines.append("")
            
            # Property-specific availability
            lines.append("🏢 Availability by Property:")
            for prop_name, avail_data in property_availability.items():
                available = avail_data['available']
                total = avail_data['total']
                percentage = (available / total) * 100 if total > 0 else 0
                lines.append(f"   • {prop_name}: {available}/{total} available ({percentage:.1f}%)")
            
            lines.append("")
            
            # Available units by bedroom count
            available_plans = [fp for fp in floor_plans if fp.availability.lower() not in ['not available', 'unavailable']]
            bedroom_availability = {}
            for fp in available_plans:
                bedroom_key = "Studio" if fp.bedrooms == 0 else f"{fp.bedrooms} Bed"
                if bedroom_key not in bedroom_availability:
                    bedroom_availability[bedroom_key] = 0
                bedroom_availability[bedroom_key] += 1
            
            lines.append("🛏️ Available Units by Type:")
            for bedroom_type, count in sorted(bedroom_availability.items()):
                lines.append(f"   • {bedroom_type}: {count} available")
            
            result = '\n'.join(lines)
            logger.info("✅ Availability report generated")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating availability report: {str(e)}")
            return f"❌ Error generating report: {str(e)}"
    
    @staticmethod
    def generate_executive_summary(floor_plans: List[FloorPlan], scraping_results: List[ScrapingResult]) -> str:
        """Generate a brief executive summary for quick overview"""
        try:
            if not floor_plans:
                return "❌ No data available for executive summary."
            
            # Calculate key metrics
            total_properties = len(set(fp.property_name for fp in floor_plans))
            total_units = len(floor_plans)
            available_units = len([fp for fp in floor_plans if fp.availability.lower() not in ['not available', 'unavailable']])
            
            prices = [fp.price for fp in floor_plans if fp.price > 0]
            avg_price = sum(prices) / len(prices) if prices else 0
            min_price = min(prices) if prices else 0
            max_price = max(prices) if prices else 0
            
            sqft_prices = [fp.price_per_sq_ft for fp in floor_plans if fp.price_per_sq_ft > 0]
            avg_sqft_price = sum(sqft_prices) / len(sqft_prices) if sqft_prices else 0
            
            # Success rate
            successful_scrapes = len([sr for sr in scraping_results if sr.success])
            success_rate = (successful_scrapes / len(scraping_results)) * 100 if scraping_results else 0
            
            lines = [
                "📋 EXECUTIVE SUMMARY",
                "=" * 30,
                f"📅 {date.today().isoformat()}",
                "",
                "🎯 Key Metrics:",
                f"   • Properties Monitored: {total_properties}",
                f"   • Total Units Found: {total_units}",
                f"   • Available Units: {available_units} ({(available_units/total_units)*100:.1f}%)",
                f"   • Scraping Success Rate: {success_rate:.1f}%",
                "",
                "💰 Pricing Overview:",
                f"   • Price Range: {ReportGenerator.format_currency(min_price)} - {ReportGenerator.format_currency(max_price)}",
                f"   • Average Price: {ReportGenerator.format_currency(avg_price)}",
                f"   • Avg Price/Sq Ft: ${avg_sqft_price:.2f}",
            ]
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"❌ Error generating executive summary: {str(e)}")
            return f"❌ Error generating summary: {str(e)}"


# Create default report service instance
default_report_service = ReportService()
