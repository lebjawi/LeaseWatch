"""
Report Generator
Creates formatted reports from apartment data
"""

from typing import List, Optional
from datetime import datetime
from ..types.types import FloorPlan, PropertySummary, DailyReport, ReportMetrics, BedroomDistribution


class ReportGenerator:
    """
    Utility class for generating formatted reports from apartment data
    """
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format currency values"""
        return f"${amount:,.0f}"

    @staticmethod
    def format_square_footage(sqft: int) -> str:
        """Format square footage"""
        return f"{sqft:,} sq ft"

    @staticmethod
    def format_bed_bath(bedrooms: int, bathrooms: float) -> str:
        """Format bedroom/bathroom count"""
        bed_str = "Studio" if bedrooms == 0 else f"{bedrooms} Bed"
        bath_str = f"{bathrooms:g} Bath"  # :g removes unnecessary decimal zeros
        return f"{bed_str} / {bath_str}" if bedrooms == 0 else f"{bed_str} / {bath_str}"

    @staticmethod
    def generate_floor_plan_report(floor_plan: FloorPlan) -> str:
        """Generate detailed floor plan report"""
        lines = [
            f"🏠 {floor_plan.name} ({floor_plan.property_name})",
            f"   💰 Price: {ReportGenerator.format_currency(floor_plan.price)}",
            f"   🛏️  Layout: {ReportGenerator.format_bed_bath(floor_plan.bedrooms, floor_plan.bathrooms)}",
            f"   📐 Size: {ReportGenerator.format_square_footage(floor_plan.square_footage)}",
            f"   💵 Price/sq ft: ${floor_plan.price_per_sq_ft}/sq ft",
            f"   🏠 Type: {floor_plan.unit_type}",
            f"   📅 Available: {floor_plan.availability}",
        ]
        
        if floor_plan.move_in_date:
            lines.append(f"   🚚 Move-in: {floor_plan.move_in_date}")
        
        if floor_plan.description:
            lines.append(f"   📝 Description: {floor_plan.description}")
        
        if floor_plan.amenities:
            lines.append(f"   ✨ Amenities: {', '.join(floor_plan.amenities[:3])}{'...' if len(floor_plan.amenities) > 3 else ''}")
        
        return '\n'.join(lines)

    @staticmethod
    def generate_property_summary_report(summary: PropertySummary) -> str:
        """Generate property summary report"""
        lines = [
            f"\n🏢 {summary.property_name}",
            f"   📊 Total Floor Plans: {summary.total_floor_plans}",
            f"   💰 Price Range: {ReportGenerator.format_currency(summary.price_range.min)} - {ReportGenerator.format_currency(summary.price_range.max)}",
            f"   💵 Avg Price/sq ft: ${summary.avg_price_per_sq_ft}/sq ft",
            f"   🏠 Available Units: {summary.available_units}",
            "",
            "   🛏️  Bedroom Distribution:",
            f"      Studio: {summary.bedroom_distribution.studio}",
            f"      1 Bed: {summary.bedroom_distribution.one_bed}",
            f"      2 Bed: {summary.bedroom_distribution.two_bed}",
            f"      3 Bed: {summary.bedroom_distribution.three_bed}",
            f"      4+ Bed: {summary.bedroom_distribution.four_plus_bed}",
        ]
        
        return '\n'.join(lines)

    @staticmethod
    def generate_daily_summary(floor_plans: List[FloorPlan]) -> str:
        """Generate daily summary report"""
        if not floor_plans:
            return "❌ No floor plans found today."
        
        total_plans = len(floor_plans)
        properties = list(set(fp.property_name for fp in floor_plans))
        prices = [fp.price for fp in floor_plans if fp.price > 0]
        
        if not prices:
            return "❌ No valid pricing data found."
        
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        # Count by bedrooms
        bedroom_counts = {}
        for fp in floor_plans:
            bed_key = "Studio" if fp.bedrooms == 0 else f"{fp.bedrooms} Bed"
            bedroom_counts[bed_key] = bedroom_counts.get(bed_key, 0) + 1
        
        lines = [
            "📊 DAILY SUMMARY",
            "=" * 50,
            f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"🏢 Properties Scraped: {len(properties)}",
            f"📋 Total Floor Plans: {total_plans}",
            f"💰 Price Range: {ReportGenerator.format_currency(min_price)} - {ReportGenerator.format_currency(max_price)}",
            f"💵 Average Price: {ReportGenerator.format_currency(avg_price)}",
            "",
            "🏠 Properties:",
        ]
        
        for prop in properties:
            prop_plans = [fp for fp in floor_plans if fp.property_name == prop]
            lines.append(f"   • {prop}: {len(prop_plans)} floor plans")
        
        lines.append("")
        lines.append("🛏️  Floor Plan Types:")
        for bed_type, count in sorted(bedroom_counts.items()):
            lines.append(f"   • {bed_type}: {count}")
        
        return '\n'.join(lines)

    @staticmethod
    def generate_comparison_report(floor_plans: List[FloorPlan], bedroom_filter: Optional[int] = None) -> str:
        """Generate comparison report, optionally filtered by bedroom count"""
        if bedroom_filter is not None:
            filtered_plans = [fp for fp in floor_plans if fp.bedrooms == bedroom_filter]
            title = f"🔍 {bedroom_filter if bedroom_filter > 0 else 'Studio'} Bedroom Comparison"
        else:
            filtered_plans = floor_plans
            title = "🔍 All Floor Plans Comparison"
        
        if not filtered_plans:
            return f"{title}\n❌ No matching floor plans found."
        
        # Sort by price per square foot for best value comparison
        sorted_plans = sorted(filtered_plans, key=lambda x: x.price_per_sq_ft if x.price_per_sq_ft > 0 else float('inf'))
        
        lines = [
            title,
            "=" * 50,
            "",
            "💡 Best Value (by price per sq ft):",
        ]
        
        for i, fp in enumerate(sorted_plans[:5], 1):  # Top 5 best values
            lines.append(f"{i}. {fp.name} ({fp.property_name})")
            lines.append(f"   💰 {ReportGenerator.format_currency(fp.price)} | ${fp.price_per_sq_ft}/sq ft | {ReportGenerator.format_square_footage(fp.square_footage)}")
            lines.append("")
        
        # Cheapest overall
        cheapest = min(filtered_plans, key=lambda x: x.price)
        lines.extend([
            "💸 Cheapest Option:",
            f"   {cheapest.name} ({cheapest.property_name})",
            f"   💰 {ReportGenerator.format_currency(cheapest.price)}",
            ""
        ])
        
        # Largest space
        largest = max(filtered_plans, key=lambda x: x.square_footage)
        lines.extend([
            "📐 Largest Space:",
            f"   {largest.name} ({largest.property_name})",
            f"   📐 {ReportGenerator.format_square_footage(largest.square_footage)} | 💰 {ReportGenerator.format_currency(largest.price)}",
        ])
        
        return '\n'.join(lines)

    @staticmethod
    def generate_error_report(errors: List[str]) -> str:
        """Generate error summary report"""
        if not errors:
            return "✅ No errors encountered during scraping."
        
        lines = [
            "❌ SCRAPING ERRORS",
            "=" * 50,
            ""
        ]
        
        for i, error in enumerate(errors, 1):
            lines.append(f"{i}. {error}")
        
        return '\n'.join(lines)

    @staticmethod
    def calculate_report_metrics(floor_plans: List[FloorPlan]) -> ReportMetrics:
        """Calculate comprehensive metrics for reporting"""
        if not floor_plans:
            return ReportMetrics(
                total_floor_plans=0,
                avg_price=0.0,
                avg_price_per_sq_ft=0.0,
                most_expensive_unit=None,
                cheapest_unit=None,
                bedroom_breakdown=BedroomDistribution()
            )
        
        prices = [fp.price for fp in floor_plans if fp.price > 0]
        price_per_sqft = [fp.price_per_sq_ft for fp in floor_plans if fp.price_per_sq_ft > 0]
        
        # Find most expensive and cheapest
        most_expensive = max(floor_plans, key=lambda x: x.price)
        cheapest = min(floor_plans, key=lambda x: x.price if x.price > 0 else float('inf'))
        
        # Calculate bedroom breakdown
        bedroom_breakdown = BedroomDistribution()
        for fp in floor_plans:
            if fp.bedrooms == 0:
                bedroom_breakdown.studio += 1
            elif fp.bedrooms == 1:
                bedroom_breakdown.one_bed += 1
            elif fp.bedrooms == 2:
                bedroom_breakdown.two_bed += 1
            elif fp.bedrooms == 3:
                bedroom_breakdown.three_bed += 1
            else:
                bedroom_breakdown.four_plus_bed += 1
        
        return ReportMetrics(
            total_floor_plans=len(floor_plans),
            avg_price=round(sum(prices) / len(prices), 2) if prices else 0.0,
            avg_price_per_sq_ft=round(sum(price_per_sqft) / len(price_per_sqft), 2) if price_per_sqft else 0.0,
            most_expensive_unit=most_expensive,
            cheapest_unit=cheapest,
            bedroom_breakdown=bedroom_breakdown
        )
