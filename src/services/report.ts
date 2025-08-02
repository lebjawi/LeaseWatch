/**
 * Report Service
 * Handles generating and formatting reports from scraped data
 */

import { DailyReport, ScrapingResult, CamdenUnit, PerimeterUnit } from '../types/types';

export class ReportService {
  
  generateDailyReport(camdenResult: ScrapingResult, perimeterResult: ScrapingResult): DailyReport {
    const camdenData = camdenResult.data as CamdenUnit[];
    const perimeterData = perimeterResult.data as PerimeterUnit[];
    
    const report: DailyReport = {
      date: new Date().toISOString(),
      camdenData,
      perimeterData,
      summary: this.generateSummary(camdenData, perimeterData)
    };

    return report;
  }

  private generateSummary(camdenData: CamdenUnit[], perimeterData: PerimeterUnit[]) {
    const allUnits = [...camdenData, ...perimeterData];
    const totalUnits = allUnits.length;

    // Filter 1-bedroom and 2-bedroom units
    const oneBedUnits = allUnits.filter(unit => 
      unit.beds.includes('1') && !unit.beds.includes('2')
    );
    const twoBedUnits = allUnits.filter(unit => 
      unit.beds.includes('2')
    );

    // Calculate average prices
    const avgPrice1Bed = this.calculateAveragePrice(oneBedUnits);
    const avgPrice2Bed = this.calculateAveragePrice(twoBedUnits);

    return {
      totalUnits,
      avgPrice1Bed,
      avgPrice2Bed
    };
  }

  private calculateAveragePrice(units: (CamdenUnit | PerimeterUnit)[]): string {
    if (units.length === 0) return 'N/A';

    const prices = units
      .map(unit => this.extractPriceNumber(unit.price))
      .filter(price => price > 0);

    if (prices.length === 0) return 'N/A';

    const average = prices.reduce((sum, price) => sum + price, 0) / prices.length;
    return `$${Math.round(average).toLocaleString()}`;
  }

  private extractPriceNumber(priceString: string): number {
    // Extract numeric value from price string like "$1,480" or "$1480"
    const match = priceString.match(/\$?([0-9,]+)/);
    if (!match || !match[1]) return 0;
    
    return parseInt(match[1].replace(/,/g, ''), 10);
  }

  formatReportForConsole(report: DailyReport): string {
    const lines = [
      '📊 DAILY APARTMENT PRICING REPORT',
      '═'.repeat(50),
      `📅 Date: ${new Date(report.date).toLocaleDateString()}`,
      '',
      '🏢 CAMDEN DUNWOODY',
      '─'.repeat(30),
      ...report.camdenData.map(unit => 
        `• ${unit.name} (${unit.beds}) - ${unit.price}`
      ),
      '',
      '🏢 PERIMETER GARDENS',
      '─'.repeat(30),
      ...report.perimeterData.map(unit => 
        `• ${unit.name} (${unit.beds}) - ${unit.price}`
      ),
      '',
      '📈 SUMMARY',
      '─'.repeat(30),
      `Total Units: ${report.summary.totalUnits}`,
      `Avg 1-Bedroom: ${report.summary.avgPrice1Bed}`,
      `Avg 2-Bedroom: ${report.summary.avgPrice2Bed}`,
      '═'.repeat(50)
    ];

    return lines.join('\n');
  }
}
