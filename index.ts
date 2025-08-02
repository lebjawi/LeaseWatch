/**
 * LeaseWatch - Automated Apartment Pricing Tracker
 * Entry point for the application
 */

import { scrapeCamden } from './src/scrapers/camden';
import { scrapeColumns } from './src/scrapers/columns';
import { scrapeDrift } from './src/scrapers/drift';
import { DataProcessor } from './src/utils/dataProcessor';
import { ReportGenerator } from './src/utils/reportGenerator';
import { FloorPlan, ScrapingResult } from './src/types/types';

async function main(): Promise<void> {
  try {
    console.log('🏡 LeaseWatch - Starting apartment pricing tracker...');
    console.log(`📅 Date: ${new Date().toISOString()}`);
    
    const allFloorPlans: FloorPlan[] = [];
    const scrapingResults: ScrapingResult[] = [];
    
    // Phase 1: Run scrapers and collect data
    console.log('\n🔍 Phase 1: Data Collection');
    console.log('=' .repeat(50));
    
    try {
      const camdenPlans = await scrapeCamden();
      allFloorPlans.push(...camdenPlans);
      scrapingResults.push({
        success: true,
        message: 'Camden scraping completed successfully',
        timestamp: new Date().toISOString(),
        source: 'Camden Dunwoody',
        floorPlans: camdenPlans,
        errors: []
      });
    } catch (error) {
      console.error('❌ Camden scraping failed:', error);
      scrapingResults.push({
        success: false,
        message: `Camden scraping failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
        source: 'Camden Dunwoody',
        floorPlans: [],
        errors: [error instanceof Error ? error.message : 'Unknown error']
      });
    }
    
    try {
      const columnsPlans = await scrapeColumns();
      allFloorPlans.push(...columnsPlans);
      scrapingResults.push({
        success: true,
        message: 'Columns scraping completed successfully',
        timestamp: new Date().toISOString(),
        source: 'The Columns at Lake Ridge',
        floorPlans: columnsPlans,
        errors: []
      });
    } catch (error) {
      console.error('❌ Columns scraping failed:', error);
      scrapingResults.push({
        success: false,
        message: `Columns scraping failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
        source: 'The Columns at Lake Ridge',
        floorPlans: [],
        errors: [error instanceof Error ? error.message : 'Unknown error']
      });
    }
    
    try {
      const driftPlans = await scrapeDrift();
      allFloorPlans.push(...driftPlans);
      scrapingResults.push({
        success: true,
        message: 'Drift scraping completed successfully',
        timestamp: new Date().toISOString(),
        source: 'Drift Dunwoody',
        floorPlans: driftPlans,
        errors: []
      });
    } catch (error) {
      console.error('❌ Drift scraping failed:', error);
      scrapingResults.push({
        success: false,
        message: `Drift scraping failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
        source: 'Drift Dunwoody',
        floorPlans: [],
        errors: [error instanceof Error ? error.message : 'Unknown error']
      });
    }
    
    // Phase 2: Process and analyze data
    console.log('\n📊 Phase 2: Data Analysis');
    console.log('=' .repeat(50));
    
    if (allFloorPlans.length === 0) {
      console.log('❌ No floor plans found. Check scraping results.');
      return;
    }
    
    // Create property summaries
    const propertySummaries = [];
    const camdenPlans = allFloorPlans.filter(fp => fp.propertyName === 'Camden Dunwoody');
    const columnsPlans = allFloorPlans.filter(fp => fp.propertyName === 'The Columns at Lake Ridge');
    
    if (camdenPlans.length > 0) {
      propertySummaries.push(DataProcessor.createPropertySummary('Camden Dunwoody', camdenPlans));
    }
    
    if (columnsPlans.length > 0) {
      propertySummaries.push(DataProcessor.createPropertySummary('The Columns at Lake Ridge', columnsPlans));
    }
    
    // Create daily report
    const dailyReport = DataProcessor.createDailyReport(propertySummaries, allFloorPlans);
    
    // Phase 3: Generate reports
    console.log('\n📋 Phase 3: Report Generation');
    console.log('=' .repeat(50));
    
    // Generate and display comprehensive report
    const report = ReportGenerator.generateDailyReport(dailyReport);
    console.log(report);
    
    // Generate comparison report if multiple properties
    if (propertySummaries.length > 1) {
      const comparison = ReportGenerator.generateComparisonReport(propertySummaries);
      console.log(comparison);
    }
    
    // Summary statistics
    console.log('\n✅ SCRAPING SUMMARY');
    console.log('=' .repeat(50));
    scrapingResults.forEach(result => {
      const status = result.success ? '✅' : '❌';
      console.log(`${status} ${result.source}: ${result.floorPlans.length} floor plans`);
      if (!result.success) {
        console.log(`   Error: ${result.message}`);
      }
    });
    
    console.log(`\n🎉 LeaseWatch completed successfully!`);
    console.log(`📊 Total floor plans tracked: ${allFloorPlans.length}`);
    console.log(`🏢 Properties monitored: ${propertySummaries.length}`);
    
  } catch (error) {
    console.error('❌ Error running LeaseWatch:', error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
}

// Run the application
if (require.main === module) {
  main().catch((error) => {
    console.error('❌ Unhandled error:', error);
    process.exit(1);
  });
}

export { main };
