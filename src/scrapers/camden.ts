/**
 * Camden Dunwoody Scraper
 * Handles scraping apartment data from Camden Living website
 */

import { chromium } from 'playwright';
import { FloorPlan } from '../types/types';
import { DataProcessor } from '../utils/dataProcessor';

export async function scrapeCamden(): Promise<FloorPlan[]> {
  console.log('🏢 Scraping Camden...');
  
  let browser;
  
  try {
    // Launch browser
    console.log('🚀 Launching Camden browser...');
    browser = await chromium.launch({
      headless: true // Run in headless mode
    });
    
    const page = await browser.newPage();
    
    // Set user agent to avoid detection
    await page.setExtraHTTPHeaders({
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    });
    
    console.log('📍 Navigating to Camden Dunwoody website...');
    
    // Navigate to Camden Dunwoody apartments page
    await page.goto('https://www.camdenliving.com/apartments/dunwoody-ga/camden-dunwoody/available-apartments', {
      waitUntil: 'domcontentloaded',
      timeout: 15000
    });
    
    // Wait a bit for dynamic content to load
    await page.waitForTimeout(3000);
    
    // Get and log the page title
    const title = await page.title();
    console.log(`✅ Camden page loaded successfully! Title: "${title}"`);
    
    // Check if page has expected content
    const url = page.url();
    console.log(`📍 Current URL: ${url}`);
    
    // Extract floor plan data
    console.log('🔍 Extracting floor plan data...');
    const floorPlans = await extractCamdenFloorPlans(page);
    
    // Log the extracted data
    console.log(`📊 Found ${floorPlans.length} floor plans`);
    
    return floorPlans;
    
  } catch (error) {
    console.error('❌ Error scraping Camden:', error instanceof Error ? error.message : 'Unknown error');
    return [];
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔒 Camden browser closed');
    }
  }
}

async function extractCamdenFloorPlans(page: any): Promise<FloorPlan[]> {
  try {
    // Wait for floor plan cards to load - using the actual Camden class names
    await page.waitForSelector('.floorplan-card, [class*="floorplan-card"]', { timeout: 10000 });
    
    // First, try to navigate to amenities section to get community amenities
    let communityAmenities: string[] = [];
    try {
      const amenitiesLink = await page.$('#community-navigation-amenities-camden-dunwoody, a[href="#amenities"]');
      if (amenitiesLink) {
        console.log('📍 Found amenities navigation, clicking to load amenities section...');
        await amenitiesLink.click();
        await page.waitForTimeout(2000); // Wait for amenities to load
        
        // Extract community amenities
        communityAmenities = await page.evaluate(() => {
          const amenitiesSection = document.querySelector('#amenities, [id*="amenities"]');
          const amenities: string[] = [];
          
          if (amenitiesSection) {
            // Look for amenity lists in the amenities section
            const amenityElements = amenitiesSection.querySelectorAll('li, .amenity, [class*="amenity"], .feature, [class*="feature"]');
            amenityElements.forEach((el: any) => {
              const text = el.textContent?.trim();
              if (text && text.length > 2 && text.length < 100 && !text.includes('Amenities')) {
                amenities.push(text);
              }
            });
          }
          
          return amenities;
        });
        
        console.log(`🏢 Found ${communityAmenities.length} community amenities`);
      }
    } catch (error) {
      console.log('⚠️ Could not navigate to amenities section, will extract from floor plan cards only');
    }
    
    const rawFloorPlans = await page.evaluate((communityAmenities: string[]) => {
      // Get all floor plan cards using the actual Camden class structure
      const floorPlanCards = Array.from(document.querySelectorAll('.floorplan-card, [class*="floorplan-card"]'));
      
      return floorPlanCards.map((card: any) => {
        // Extract floor plan name from h1 with specific classes
        let name = '';
        const nameEl = card.querySelector('h1.my-4.font-sans.font-extrabold, h1[class*="font-extrabold"], h1[class*="my-4"]');
        if (nameEl && nameEl.textContent?.trim()) {
          name = nameEl.textContent.trim();
        }
        
        // Fallback: try other heading selectors
        if (!name) {
          const headingEl = card.querySelector('h1, h2, h3, .plan-name, [class*="plan-name"]');
          if (headingEl && headingEl.textContent?.trim()) {
            name = headingEl.textContent.trim();
          }
        }
        
        // Extract price - look for dollar signs
        let price = '';
        const priceSelectors = [
          '[class*="price"]',
          '[class*="rent"]', 
          '[class*="cost"]'
        ];
        
        for (const selector of priceSelectors) {
          const priceEl = card.querySelector(selector);
          if (priceEl && priceEl.textContent?.includes('$')) {
            price = priceEl.textContent.trim();
            break;
          }
        }
        
        // If no price found in specific elements, search all text for $ pattern
        if (!price) {
          const allText = card.textContent || '';
          const priceMatch = allText.match(/\$[\d,]+[+]?/);
          if (priceMatch) {
            price = priceMatch[0];
          }
        }
        
        // Extract bed/bath count from the specific container with icons
        let bedBathCount = '';
        let squareFootage = '';
        
        // Look for the container with bed, bath, and sqft info
        const infoContainer = card.querySelector('.flex.flex-row.items-center.justify-between.w-full.font-bold, [class*="jsx-"][class*="flex"][class*="flex-row"]');
        
        if (infoContainer) {
          // Extract bed count
          const bedSpan = infoContainer.querySelector('span img[alt="Bed"], span img[src*="bed.svg"]');
          if (bedSpan && bedSpan.parentElement) {
            const bedText = bedSpan.parentElement.textContent?.trim();
            if (bedText) {
              const bedMatch = bedText.match(/(\d+)\s*Bed/i);
              if (bedMatch) {
                const bedCount = bedMatch[1];
                
                // Extract bath count
                const bathSpan = infoContainer.querySelector('span img[alt="Bath"], span img[src*="bath.svg"]');
                if (bathSpan && bathSpan.parentElement) {
                  const bathText = bathSpan.parentElement.textContent?.trim();
                  if (bathText) {
                    const bathMatch = bathText.match(/(\d+)\s*Bath/i);
                    if (bathMatch) {
                      const bathCount = bathMatch[1];
                      bedBathCount = `${bedCount} Bed / ${bathCount} Bath`;
                    }
                  }
                }
              }
            }
          }
          
          // Extract square footage from the same container
          const sqftSpan = infoContainer.querySelector('span img[alt="Floorplan"], span img[src*="floorplan.svg"]');
          if (sqftSpan && sqftSpan.parentElement) {
            const sqftText = sqftSpan.parentElement.textContent?.trim();
            if (sqftText && sqftText.includes('SqFt')) {
              squareFootage = sqftText;
            }
          }
        }
        
        // Fallback: Extract bed/bath count using previous methods if not found
        if (!bedBathCount) {
          const bedBathSelectors = [
            '[class*="bed"]',
            '[class*="bath"]',
            '[class*="bedroom"]',
            '[class*="bathroom"]'
          ];
          
          for (const selector of bedBathSelectors) {
            const bedBathEl = card.querySelector(selector);
            if (bedBathEl && (bedBathEl.textContent?.includes('bed') || bedBathEl.textContent?.includes('bath'))) {
              bedBathCount = bedBathEl.textContent.trim();
              break;
            }
          }
        }
        
        // Fallback: search for bed/bath pattern in all text
        if (!bedBathCount) {
          const allText = card.textContent || '';
          const bedBathMatch = allText.match(/(\d+)\s*bed[s]?\s*[\/\|,\s]+(\d+)\s*bath[s]?/i) || 
                               allText.match(/(\d+)\s*br?\s*[\/\|,\s]+(\d+)\s*ba?/i) ||
                               allText.match(/(\d+)\s*bedroom[s]?\s*[\/\|,\s]+(\d+)\s*bathroom[s]?/i);
          if (bedBathMatch) {
            bedBathCount = `${bedBathMatch[1]} Bed / ${bedBathMatch[2]} Bath`;
          }
        }
        
        // Fallback: Extract square footage if not found in the info container
        if (!squareFootage) {
          const sqftSelectors = [
            'span.flex:has(img[alt="Floorplan"])',
            'span.flex',
            '[class*="sqft"]',
            '[class*="square"]'
          ];
          
          for (const selector of sqftSelectors) {
            const sqftEl = card.querySelector(selector);
            if (sqftEl && sqftEl.textContent?.includes('SqFt')) {
              squareFootage = sqftEl.textContent.trim();
              break;
            }
          }
        }
        
        // Final fallback: search for SqFt pattern in all text
        if (!squareFootage) {
          const allText = card.textContent || '';
          const sqftMatch = allText.match(/(\d+[,\d]*)\s*SqFt/i) || 
                           allText.match(/(\d+[,\d]*)\s*sq\.?\s*ft\.?/i) ||
                           allText.match(/(\d+[,\d]*)\s*square\s*feet/i);
          if (sqftMatch) {
            squareFootage = sqftMatch[0];
          }
        }
        
        // Extract amenities - combine unit-specific and community amenities
        const amenities: string[] = [...communityAmenities]; // Start with community amenities
        const amenitySelectors = [
          '[class*="amenity"]',
          '[class*="feature"]',
          '[class*="highlight"]',
          'ul li',
          '.amenity-list li',
          '.feature-list li'
        ];
        
        for (const selector of amenitySelectors) {
          const amenityElements = card.querySelectorAll(selector);
          amenityElements.forEach((el: any) => {
            const text = el.textContent?.trim();
            if (text && text.length > 0 && text.length < 100 && !amenities.includes(text)) { // Avoid duplicates
              amenities.push(text);
            }
          });
        }
        
        // Extract availability date
        let availability = '';
        const availabilitySelectors = [
          'p[class*="jsx-"]', // Look for paragraph elements with jsx classes
          'p',
          '[class*="availability"]',
          '[class*="date"]'
        ];
        
        for (const selector of availabilitySelectors) {
          const availabilityEl = card.querySelector(selector);
          if (availabilityEl && availabilityEl.textContent?.trim()) {
            const text = availabilityEl.textContent.trim();
            // Check if text looks like a date (MM/DD/YYYY format)
            if (text.match(/^\d{1,2}\/\d{1,2}\/\d{4}$/)) {
              availability = text;
              break;
            }
          }
        }
        
        // If no specific availability date found, look for text patterns
        if (!availability) {
          const allText = card.textContent || '';
          const dateMatch = allText.match(/(\d{1,2}\/\d{1,2}\/\d{4})/);
          if (dateMatch) {
            availability = dateMatch[1];
          }
        }
        
        return {
          name: name || 'Unknown Plan',
          price: price || 'Price not available',
          bedBathCount: bedBathCount || 'Not specified',
          squareFootage: squareFootage || 'Not specified',
          amenities: [...new Set(amenities)], // Remove duplicates
          availability: availability || 'Not specified'
        };
      }).filter((plan: any) => 
        // Filter out cards that don't have essential data
        plan.name !== 'Unknown Plan' && plan.name.length > 0
      );
    }, communityAmenities); // Pass communityAmenities to the page.evaluate function
    
    // Process the raw data into enhanced FloorPlan objects
    const enhancedFloorPlans: FloorPlan[] = rawFloorPlans.map((rawPlan: any) => {
      const price = DataProcessor.parsePrice(rawPlan.price);
      const bedrooms = DataProcessor.parseBedrooms(rawPlan.bedBathCount);
      const bathrooms = DataProcessor.parseBathrooms(rawPlan.bedBathCount);
      const squareFootage = DataProcessor.parseSquareFootage(rawPlan.squareFootage);
      const cleanName = DataProcessor.cleanFloorPlanName(rawPlan.name);
      const unitType = DataProcessor.determineUnitType(rawPlan.name, bathrooms);
      const pricePerSqFt = DataProcessor.calculatePricePerSqFt(price, squareFootage);
      const availability = DataProcessor.standardizeAvailability(rawPlan.availability);
      
      return {
        name: cleanName,
        price: price,
        bedrooms: bedrooms,
        bathrooms: bathrooms,
        squareFootage: squareFootage,
        pricePerSqFt: pricePerSqFt,
        amenities: rawPlan.amenities,
        availability: availability,
        propertyName: 'Camden Dunwoody',
        propertyUrl: 'https://www.camdenliving.com/apartments/dunwoody-ga/camden-dunwoody/available-apartments',
        unitType: unitType,
        moveInDate: rawPlan.availability.match(/\d{1,2}\/\d{1,2}\/\d{4}/) ? rawPlan.availability : undefined
      };
    });
    
    return enhancedFloorPlans;
  } catch (error) {
    console.error('❌ Error extracting Camden floor plans:', error);
    return [];
  }
}
