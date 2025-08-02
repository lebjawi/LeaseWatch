/**
 * Report Generator
 * Creates formatted reports from apartment data
 */

import { FloorPlan, PropertySummary, DailyReport } from '../types/types';

export class ReportGenerator {
  
  /**
   * Format currency values
   */
  static formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  /**
   * Format square footage
   */
  static formatSquareFootage(sqft: number): string {
    return `${sqft.toLocaleString()} sq ft`;
  }

  /**
   * Format bedroom/bathroom count
   */
  static formatBedBath(bedrooms: number, bathrooms: number): string {
    const bedStr = bedrooms === 0 ? 'Studio' : `${bedrooms} Bed`;
    const bathStr = bathrooms % 1 === 0 ? `${bathrooms} Bath` : `${bathrooms} Bath`;
    return bedrooms === 0 ? `${bedStr} / ${bathStr}` : `${bedStr} / ${bathStr}`;
  }

  /**
   * Generate detailed floor plan report
   */
  static generateFloorPlanReport(floorPlan: FloorPlan): string {
    const lines = [
      `🏠 ${floorPlan.name} (${floorPlan.propertyName})`,
      `   💰 Price: ${this.formatCurrency(floorPlan.price)}`,
      `   🛏️  Layout: ${this.formatBedBath(floorPlan.bedrooms, floorPlan.bathrooms)}`,
      `   📐 Size: ${this.formatSquareFootage(floorPlan.squareFootage)}`,
      `   💵 Price/sq ft: $${floorPlan.pricePerSqFt}/sq ft`,
      `   🏠 Type: ${floorPlan.unitType}`,
      `   📅 Available: ${floorPlan.availability}`,
    ];

    if (floorPlan.amenities.length > 0) {
      lines.push(`   ✨ Amenities: ${floorPlan.amenities.join(', ')}`);
    }

    return lines.join('\n');
  }

  /**
   * Generate property summary report
   */
  static generatePropertySummary(summary: PropertySummary): string {
    const lines = [
      `\n🏢 ${summary.propertyName}`,
      `   📊 ${summary.totalFloorPlans} floor plans available`,
      `   💰 Price range: ${this.formatCurrency(summary.priceRange.min)} - ${this.formatCurrency(summary.priceRange.max)}`,
      `   💵 Avg price/sq ft: $${summary.avgPricePerSqFt}/sq ft`,
      `   🏠 Available units: ${summary.availableUnits}`,
      `   🛏️  Unit distribution:`,
    ];

    const dist = summary.bedroomDistribution;
    if (dist.studio > 0) lines.push(`      • Studio: ${dist.studio}`);
    if (dist.oneBed > 0) lines.push(`      • 1 Bedroom: ${dist.oneBed}`);
    if (dist.twoBed > 0) lines.push(`      • 2 Bedroom: ${dist.twoBed}`);
    if (dist.threeBed > 0) lines.push(`      • 3 Bedroom: ${dist.threeBed}`);
    if (dist.fourPlusBed > 0) lines.push(`      • 4+ Bedroom: ${dist.fourPlusBed}`);

    return lines.join('\n');
  }

  /**
   * Generate comprehensive daily report
   */
  static generateDailyReport(report: DailyReport): string {
    const lines = [
      `\n📋 LEASEWATCH DAILY REPORT - ${report.date}`,
      `${'='.repeat(60)}`,
      `\n📈 MARKET SUMMARY`,
      `   🏠 Total units tracked: ${report.marketSummary.totalUnits}`,
      `   💰 Average rent: ${this.formatCurrency(report.marketSummary.avgRent)}`,
      `   💵 Market avg price/sq ft: $${report.marketSummary.avgPricePerSqFt}/sq ft`,
      `\n🏆 MARKET HIGHLIGHTS`,
      `   💸 Most affordable: ${report.marketSummary.cheapestUnit.name} - ${this.formatCurrency(report.marketSummary.cheapestUnit.price)}`,
      `   💎 Most expensive: ${report.marketSummary.mostExpensiveUnit.name} - ${this.formatCurrency(report.marketSummary.mostExpensiveUnit.price)}`,
      `   🎯 Best value: ${report.marketSummary.bestValueUnit.name} - $${report.marketSummary.bestValueUnit.pricePerSqFt}/sq ft`,
      `\n🏢 PROPERTY SUMMARIES`,
    ];

    // Add property summaries
    report.properties.forEach(property => {
      lines.push(this.generatePropertySummary(property));
    });

    lines.push(`\n📋 DETAILED FLOOR PLANS`);
    lines.push(`${'='.repeat(60)}`);

    // Group floor plans by property
    const floorPlansByProperty = report.allFloorPlans.reduce((acc, fp) => {
      if (!acc[fp.propertyName]) acc[fp.propertyName] = [];
      acc[fp.propertyName]!.push(fp);
      return acc;
    }, {} as Record<string, FloorPlan[]>);

    Object.entries(floorPlansByProperty).forEach(([propertyName, floorPlans]) => {
      lines.push(`\n🏢 ${propertyName.toUpperCase()}`);
      lines.push(`${'-'.repeat(40)}`);
      
      // Sort by price
      floorPlans.sort((a, b) => a.price - b.price);
      
      floorPlans.forEach(fp => {
        lines.push(this.generateFloorPlanReport(fp));
        lines.push(''); // Empty line between floor plans
      });
    });

    return lines.join('\n');
  }

  /**
   * Generate comparison report between properties
   */
  static generateComparisonReport(properties: PropertySummary[]): string {
    const lines = [
      `\n📊 PROPERTY COMPARISON`,
      `${'='.repeat(60)}`,
    ];

    // Sort by average price per sq ft
    const sortedProps = [...properties].sort((a, b) => a.avgPricePerSqFt - b.avgPricePerSqFt);

    lines.push(`\n🏆 RANKINGS BY VALUE (Price per sq ft):`);
    sortedProps.forEach((prop, index) => {
      lines.push(`   ${index + 1}. ${prop.propertyName}: $${prop.avgPricePerSqFt}/sq ft`);
    });

    lines.push(`\n💰 PRICE RANGES:`);
    properties.forEach(prop => {
      lines.push(`   ${prop.propertyName}: ${ReportGenerator.formatCurrency(prop.priceRange.min)} - ${ReportGenerator.formatCurrency(prop.priceRange.max)}`);
    });

    lines.push(`\n🏠 AVAILABLE UNITS:`);
    properties.forEach(prop => {
      lines.push(`   ${prop.propertyName}: ${prop.availableUnits} units`);
    });

    return lines.join('\n');
  }
}
