/**
 * Perimeter Gardens Scraper
 * Handles scraping apartment data from Perimeter Gardens website
 */

import puppeteer from 'puppeteer';
import { FloorPlan } from '../types/types';

export async function scrapePerimeter(): Promise<void> {
  console.log('🏢 Scraping Perimeter...');
  
  let browser;
  
  try {
    // Launch browser
    console.log('🚀 Launching Perimeter browser...');
    browser = await puppeteer.launch({
      headless: false, // Show browser window for inspection
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });
    
    const page = await browser.newPage();
    
    // Set user agent to avoid detection
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
    
    console.log('📍 Navigating to Perimeter Gardens website...');
    
    // Navigate to Perimeter Gardens interactive property map
    await page.goto('https://www.perimetergardens.com/interactivepropertymap', {
      waitUntil: 'domcontentloaded',
      timeout: 15000
    });
    
    // Wait a bit for dynamic content to load
    await page.waitForTimeout(3000);
    
    // Get and log the page title
    const title = await page.title();
    console.log(`✅ Perimeter page loaded successfully! Title: "${title}"`);
    
    // Check if page has expected content
    const url = page.url();
    console.log(`📍 Current URL: ${url}`);
    
    // Extract floor plan data
    console.log('🔍 Extracting floor plan data...');
    const floorPlans = await extractPerimeterFloorPlans(page);
    
    // Log the extracted data
    console.log(`📊 Found ${floorPlans.length} floor plans:`);
    floorPlans.forEach((plan, index) => {
      console.log(`\n🏠 Floor Plan ${index + 1}:`);
      console.log(`   Name: ${plan.name}`);
      console.log(`   Price: ${plan.price}`);
      console.log(`   Bed/Bath: ${plan.bedBathCount}`);
      console.log(`   Square Footage: ${plan.squareFootage}`);
      console.log(`   Available: ${plan.availability}`);
      console.log(`   Amenities: ${plan.amenities.join(', ') || 'None listed'}`);
    });
    
  } catch (error) {
    console.error('❌ Error scraping Perimeter:', error instanceof Error ? error.message : 'Unknown error');
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔒 Perimeter browser closed');
    }
  }
}

async function extractPerimeterFloorPlans(page: any): Promise<FloorPlan[]> {
  try {
    console.log('🗺️ Starting Perimeter Gardens navigation sequence...');
    
    // Step 1: Wait for the initial map to load and find region buttons
    console.log('📍 Step 1: Looking for region buttons...');
    await page.waitForSelector('button.ipm-popovers', { timeout: 15000 });
    
    // Get all region buttons (should be 2 regions)
    const regionButtons = await page.$$('button.ipm-popovers');
    console.log(`🏘️ Found ${regionButtons.length} regions to explore`);
    
    const allUnits: FloorPlan[] = [];
    
    // Step 2: Navigate through each region
    for (let regionIndex = 0; regionIndex < regionButtons.length; regionIndex++) {
      console.log(`\n📍 Step 2.${regionIndex + 1}: Clicking on Region ${regionIndex + 1}...`);
      
      try {
        // Click on the region button to open that region's map
        await regionButtons[regionIndex].click();
        console.log(`✅ Clicked Region ${regionIndex + 1} button`);
        await page.waitForTimeout(3000); // Wait for region map to load
        
        // Step 3: Look for available unit pins in this region
        console.log(`� Step 3.${regionIndex + 1}: Looking for available unit pins...`);
        await page.waitForSelector('button.pin.avail_unit', { timeout: 10000 });
        
        const unitPins = await page.$$('button.pin.avail_unit');
        console.log(`🏠 Found ${unitPins.length} available units in Region ${regionIndex + 1}`);
        
        // Step 4: Click on each unit pin to get details
        for (let unitIndex = 0; unitIndex < unitPins.length; unitIndex++) {
          console.log(`� Step 4.${regionIndex + 1}.${unitIndex + 1}: Clicking unit pin ${unitIndex + 1}/${unitPins.length}...`);
          
          try {
            // Click on the unit pin to open unit details
            await unitPins[unitIndex].click();
            console.log(`✅ Clicked unit pin ${unitIndex + 1}`);
            await page.waitForTimeout(2000); // Wait for unit details to load
            
            // Step 5: Extract unit information from the opened unit details page
            console.log(`📍 Step 5.${regionIndex + 1}.${unitIndex + 1}: Extracting unit information...`);
            
            const unitData = await page.evaluate(() => {
              // Extract unit name/number from <span id="unit_name">
              const unitNameEl = document.querySelector('#unit_name');
              const unitName = unitNameEl?.textContent?.trim() || '';
              
              // Extract bed information from <span id="unit_beds">
              const bedsEl = document.querySelector('#unit_beds');
              const beds = bedsEl?.textContent?.trim() || '';
              
              // Extract bath information from <span id="unit_baths">
              const bathsEl = document.querySelector('#unit_baths');
              const baths = bathsEl?.textContent?.trim() || '';
              
              // Extract floor plan from <span id="unit_floorplan">
              const floorplanEl = document.querySelector('#unit_floorplan');
              const floorplan = floorplanEl?.textContent?.trim() || '';
              
              // Extract square footage from <span id="unit_sqft">
              const sqftEl = document.querySelector('#unit_sqft');
              const sqft = sqftEl?.textContent?.trim() || '';
              
              // Extract floor from <span id="unit_floor">
              const floorEl = document.querySelector('#unit_floor');
              const floor = floorEl?.textContent?.trim() || '';
              
              // Extract price from sidebar <span class="h2 unit_price">
              const priceEl = document.querySelector('.unit_price');
              const price = priceEl?.textContent?.trim() || '';
              
              // Extract availability date from <p class="open_for_application_date">
              const availabilityEl = document.querySelector('.open_for_application_date');
              const availability = availabilityEl?.textContent?.trim() || '';
              
              return {
                unitName,
                beds,
                baths,
                floorplan,
                sqft,
                floor,
                price,
                availability
              };
            });
            
            // Process and format the extracted data
            let bedBathCount = 'Not specified';
            if (unitData.beds && unitData.baths) {
              const bedMatch = unitData.beds.match(/(\d+)/);
              const bathMatch = unitData.baths.match(/(\d+)/);
              if (bedMatch && bathMatch) {
                bedBathCount = `${bedMatch[1]} Bed / ${bathMatch[1]} Bath`;
              }
            }
            
            const squareFootage = unitData.sqft ? `${unitData.sqft} Sq. Ft.` : 'Not available';
            const floorInfo = unitData.floor ? `Floor: ${unitData.floor}` : '';
            const availability = unitData.availability && !unitData.availability.includes('d-none') ? 
              unitData.availability : 'Available Now';
            
            // Create floor plan object
            const floorPlan: FloorPlan = {
              name: `Unit ${unitData.unitName}${unitData.floorplan ? ` (${unitData.floorplan})` : ''}`,
              price: unitData.price || 'Price not available',
              bedBathCount: bedBathCount,
              squareFootage: squareFootage,
              amenities: floorInfo ? [floorInfo] : [],
              availability: availability
            };
            
            allUnits.push(floorPlan);
            console.log(`✅ Extracted data for Unit ${unitData.unitName}`);
            
            // Step 6: Close the unit details (press Escape or click elsewhere)
            console.log(`📍 Step 6.${regionIndex + 1}.${unitIndex + 1}: Closing unit details...`);
            await page.keyboard.press('Escape');
            await page.waitForTimeout(1000);
            
          } catch (unitError) {
            console.log(`❌ Error processing unit ${unitIndex + 1}:`, unitError);
            // Try to close any open dialogs and continue
            await page.keyboard.press('Escape');
            await page.waitForTimeout(500);
          }
        }
        
        // Step 7: Navigate back to main map for next region
        console.log(`📍 Step 7.${regionIndex + 1}: Navigating back to main map...`);
        
        if (regionIndex < regionButtons.length - 1) {
          // If not the last region, go back to main map
          try {
            // Try clicking a "back" button or reload the page
            await page.reload();
            await page.waitForTimeout(3000);
            console.log(`✅ Returned to main map`);
            
            // Re-get region buttons after reload
            const refreshedRegionButtons = await page.$$('button.ipm-popovers');
            // Update our reference to the buttons
            for (let i = 0; i < refreshedRegionButtons.length; i++) {
              if (i < regionButtons.length) {
                regionButtons[i] = refreshedRegionButtons[i];
              }
            }
          } catch (backError) {
            console.log(`⚠️ Error going back to main map:`, backError);
          }
        }
        
      } catch (regionError) {
        console.log(`❌ Error exploring Region ${regionIndex + 1}:`, regionError);
        // Continue with next region
      }
    }
    
    console.log(`\n🎉 Navigation complete! Collected data from ${allUnits.length} units total`);
    return allUnits;
    
  } catch (error) {
    console.error('❌ Error in Perimeter navigation sequence:', error);
    return [];
  }
}
