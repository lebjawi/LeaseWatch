/**
 * The Columns at Lake Ridge Scraper
 * Handles scraping apartment data from The Columns at Lake Ridge website
 */

import { chromium } from 'playwright';
import { FloorPlan } from '../types/types';
import { DataProcessor } from '../utils/dataProcessor';

export async function scrapeColumns(): Promise<FloorPlan[]> {
  console.log('🏢 Scraping The Columns at Lake Ridge...');
  
  let browser;
  
  try {
    // Launch browser
    console.log('🚀 Launching Columns browser...');
    browser = await chromium.launch({
      headless: true // Run in headless mode
    });
    
    const page = await browser.newPage();
    
    // Set user agent to avoid detection
    await page.setExtraHTTPHeaders({
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    });
    
    console.log('📍 Navigating to The Columns at Lake Ridge website...');
    
    // Navigate to The Columns floor plans page
    await page.goto('https://www.thecolumnsatlakeridge.com/apartments/ga/dunwoody/floor-plans#/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    
    // Wait for page to be fully loaded
    await page.waitForTimeout(5000);
    
    // Get and log the page title
    const title = await page.title();
    console.log(`✅ Columns page loaded successfully! Title: "${title}"`);
    
    // Check if page has expected content
    const url = page.url();
    console.log(`📍 Current URL: ${url}`);
    
    // Extract floor plan data
    console.log('🔍 Extracting floor plan data...');
    const floorPlans = await extractColumnsFloorPlans(page);
    
    const processedFloorPlans = floorPlans.map(plan => {
      // Extract raw text that was temporarily stored in old structure
      const rawText = (plan as any).bedBathCount || '';
      const rawPrice = (plan as any).price || '';
      const rawSqft = (plan as any).squareFootage || '';
      
      const bathrooms = DataProcessor.parseBathrooms(rawText);
      // Use original name instead of overcleaning
      const cleanName = plan.name.trim().replace(/\s+/g, ' ');
      
      return {
        name: cleanName,
        price: DataProcessor.parsePrice(rawPrice),
        bedrooms: DataProcessor.parseBedrooms(rawText),
        bathrooms: bathrooms,
        squareFootage: DataProcessor.parseSquareFootage(rawSqft),
        pricePerSqFt: 0, // Will be calculated after processing
        amenities: plan.amenities || [],
        availability: plan.availability,
        propertyName: 'The Columns at Lake Ridge',
        propertyUrl: 'https://www.thecolumnsatlakeridge.com',
        unitType: DataProcessor.determineUnitType(cleanName, bathrooms)
      };
    }).map(plan => {
      // Calculate price per square foot
      const pricePerSqFt = plan.squareFootage > 0 ? Math.round((plan.price / plan.squareFootage) * 100) / 100 : 0;
      return {
        ...plan,
        pricePerSqFt
      };
    });
    
    // Log the extracted data
    console.log(`📊 Found ${processedFloorPlans.length} floor plans:`);
    processedFloorPlans.forEach((plan, index) => {
      console.log(`\n🏠 Floor Plan ${index + 1}:`);
      console.log(`   Name: ${plan.name}`);
      console.log(`   Price: $${plan.price}`);
      console.log(`   Bedrooms: ${plan.bedrooms}`);
      console.log(`   Bathrooms: ${plan.bathrooms}`);
      console.log(`   Square Footage: ${plan.squareFootage} sq ft`);
      console.log(`   Price per Sq Ft: $${plan.pricePerSqFt}`);
      console.log(`   Available: ${plan.availability}`);
      console.log(`   Amenities: ${plan.amenities.join(', ') || 'None listed'}`);
    });
    
    return processedFloorPlans;
    
  } catch (error) {
    console.error('❌ Error scraping The Columns:', error);
    if (error instanceof Error) {
      console.error('❌ Error details:', error.message);
      console.error('❌ Stack trace:', error.stack);
    }
    return [];
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔒 Columns browser closed');
    }
  }
}

async function extractColumnsFloorPlans(page: any): Promise<any[]> {
  try {
    console.log('🏠 Starting The Columns at Lake Ridge data extraction...');
    
    // Wait for floor plan content to load
    await page.waitForTimeout(3000);
    
    // Look for common floor plan selectors
    const floorPlans: FloorPlan[] = [];
    
    // Let's first explore what's on the page
    console.log('🔍 Analyzing page structure...');
    
    // Check for common floor plan container patterns
    const possibleSelectors = [
      '.floor-plan',
      '.floorplan',
      '.apartment',
      '.unit',
      '.plan',
      '[class*="floor"]',
      '[class*="plan"]',
      '[class*="apartment"]',
      '[class*="unit"]'
    ];
    
    let floorPlanElements = [];
    let usedSelector = '';
    
    for (const selector of possibleSelectors) {
      const elements = await page.locator(selector).all();
      if (elements.length > 0) {
        console.log(`✅ Found ${elements.length} elements with selector: ${selector}`);
        floorPlanElements = elements;
        usedSelector = selector;
        break;
      }
    }
    
    if (floorPlanElements.length === 0) {
      console.log('🔍 No floor plan elements found with common selectors. Let\'s debug...');
      
      // Debug: Get all elements and their classes
      const allElements = await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('*'));
        const classNames = new Set();
        elements.forEach(el => {
          if (el.className && typeof el.className === 'string') {
            el.className.split(' ').forEach(cls => {
              if (cls.trim()) classNames.add(cls.trim());
            });
          }
        });
        return Array.from(classNames).sort();
      });
      
      console.log('🔍 Available CSS classes on page:', allElements.slice(0, 50)); // Show first 50 classes
      
      // Check page content
      const bodyText = await page.evaluate(() => {
        return document.body.textContent?.substring(0, 1000) || 'No body content';
      });
      console.log('📄 Page content preview:', bodyText);
      
      return [];
    }
    
    console.log(`📊 Processing ${floorPlanElements.length} floor plan elements...`);
    
    // Extract data from each floor plan element
    for (let i = 0; i < floorPlanElements.length; i++) {
      try {
        const element = floorPlanElements[i];
        
        // Extract text content from the element
        const elementText = await element.textContent();
        const elementHTML = await element.innerHTML();
        
        console.log(`\n🔍 Processing element ${i + 1}:`);
        console.log(`Text: ${elementText?.substring(0, 200)}...`);
        
        // Try to extract floor plan information
        const floorPlan = await extractFloorPlanFromElement(element, page);
        
        if (floorPlan) {
          floorPlans.push(floorPlan);
          console.log(`✅ Successfully extracted: ${floorPlan.name}`);
        }
        
      } catch (elementError) {
        console.log(`❌ Error processing element ${i + 1}:`, elementError);
      }
    }
    
    return floorPlans;
    
  } catch (error) {
    console.error('❌ Error extracting floor plans:', error);
    return [];
  }
}

async function extractFloorPlanFromElement(element: any, page: any): Promise<any | null> {
  try {
    // Get all text content from the element
    const textContent = await element.textContent() || '';
    
    // Look for common patterns in apartment listings
    const priceMatch = textContent.match(/\$[\d,]+/);
    const bedroomMatch = textContent.match(/(\d+)\s*(bed|bedroom|br)/i);
    const bathroomMatch = textContent.match(/(\d+)\s*(bath|bathroom|ba)/i);
    const decimalBathMatch = textContent.match(/(\d+\.5)\s*(baths?|bathrooms?|ba)/i);
    const sqftMatch = textContent.match(/(\d+(?:,\d+)?)\s*(sq\.?\s*ft|sqft|square\s*feet)/i);
    
    // Try to find a name/title
    let name = 'Unknown Plan';
    const nameElement = await element.locator('h1, h2, h3, h4, .title, .name, [class*="title"], [class*="name"]').first();
    if (await nameElement.count() > 0) {
      const nameText = await nameElement.textContent();
      if (nameText && nameText.trim()) {
        name = nameText.trim();
      }
    }
    
    // If no specific name found, try to extract just the main title
    if (name === 'Unknown Plan') {
      const lines = textContent.split('\n').filter((line: string) => line.trim());
      if (lines.length > 0) {
        // Take the first line that has bedroom/bath info and clean it
        for (const line of lines) {
          const trimmedLine = line.trim();
          if (trimmedLine && (trimmedLine.includes('Bedroom') || trimmedLine.includes('Bath'))) {
            // Clean the name - just keep the main part before any numbers/details
            name = trimmedLine.split(/\d+\s*Bed/)[0].trim() || trimmedLine;
            if (name.length < 5) { // If name is too short, use original
              name = trimmedLine;
            }
            break;
          }
        }
        
        // If still no good name, use first non-empty line but clean it
        if (name === 'Unknown Plan' && lines[0]) {
          name = lines[0].trim().substring(0, 40); // Limit length
        }
      }
    }
    
    // Fix bathroom parsing for .5 baths
    let bathCount = '?';
    if (decimalBathMatch) {
      bathCount = decimalBathMatch[1];
    } else if (bathroomMatch) {
      bathCount = bathroomMatch[1];
    }
    
    // Return a temporary structure that will be processed later
    const tempFloorPlan = {
      name: name,
      price: priceMatch ? priceMatch[0] : 'Price not available',
      bedBathCount: `${bedroomMatch ? bedroomMatch[1] : '?'} Bed / ${bathCount} Bath`,
      squareFootage: sqftMatch ? sqftMatch[1] : '0',
      amenities: [],
      availability: 'Available' // Default, could be enhanced
    };
    
    // Only return if we found at least some useful information
    if (priceMatch || bedroomMatch || sqftMatch) {
      return tempFloorPlan;
    }
    
    return null;
    
  } catch (error) {
    console.log('❌ Error extracting from element:', error);
    return null;
  }
}
