/**
 * LeaseWatch - Automated Apartment Pricing Tracker
 * Entry point for the application
 */

import { scrapeCamden } from './src/scrapers/camden';
import { scrapePerimeter } from './src/scrapers/perimeter';

async function main(): Promise<void> {
  try {
    console.log('🏡 LeaseWatch - Starting apartment pricing tracker...');
    console.log(`📅 Date: ${new Date().toISOString()}`);
    
    // Phase 1: Run scrapers - temporarily only Perimeter for testing
    // await scrapeCamden();
    await scrapePerimeter();
    
    console.log('✅ LeaseWatch completed successfully!');
    
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
