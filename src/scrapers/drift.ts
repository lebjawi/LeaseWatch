/**
 * Drift Dunwoody Scraper
 * Handles scraping apartment data from Drift Dunwoody website
 */

import { chromium } from 'playwright';
import { FloorPlan } from '../types/types';
import { DataProcessor } from '../utils/dataProcessor';

export async function scrapeDrift(): Promise<FloorPlan[]> {
  console.log('🏢 Scraping Drift Dunwoody...');
  
  let browser;
  
  try {
    // Launch browser
    console.log('🚀 Launching Drift browser...');
    browser = await chromium.launch({
      headless: true // Run in headless mode
    });
    
    const page = await browser.newPage();
    
    // Set user agent to avoid detection
    await page.setExtraHTTPHeaders({
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    });
    
    console.log('📍 Navigating to Drift Dunwoody Cobblestone app...');
    
    // Navigate directly to the Cobblestone floor plans page
    await page.goto('https://app.getcobblestone.com/complex/2oRUqV2UXteJYr25ds4syVrY5Ap/floorplans', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    
    // Wait for page to be fully loaded
    await page.waitForTimeout(5000);
    
    // Get and log the page title
    const title = await page.title();
    console.log(`✅ Drift page loaded successfully! Title: "${title}"`);
    
    // Check if page has expected content
    const url = page.url();
    console.log(`📍 Current URL: ${url}`);
    
    // Extract floor plan data
    console.log('🔍 Extracting floor plan data...');
    const floorPlans = await extractDriftFloorPlans(page);
    
    // Process and clean the data using DataProcessor
    const processedFloorPlans = floorPlans.map(plan => {
      // Extract raw text that was temporarily stored in old structure
      const rawText = (plan as any).bedBathCount || '';
      const rawPrice = (plan as any).price || '';
      const rawSqft = (plan as any).squareFootage || '';
      
      const bathrooms = DataProcessor.parseBathrooms(rawText);
      // Use original name and clean it
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
        propertyName: 'Drift Dunwoody',
        propertyUrl: 'https://www.driftdunwoody.com',
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
    console.error('❌ Error scraping Drift Dunwoody:', error);
    if (error instanceof Error) {
      console.error('❌ Error details:', error.message);
      console.error('❌ Stack trace:', error.stack);
    }
    return [];
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔒 Drift browser closed');
    }
  }
}

async function extractDriftFloorPlans(page: any): Promise<any[]> {
  try {
    console.log('🏠 Starting Drift Dunwoody data extraction...');
    
    // Wait for floor plan content to load
    await page.waitForTimeout(3000);
    
    // Look for common floor plan selectors
    const floorPlans: any[] = [];
    
    // Let's first explore what's on the page
    console.log('🔍 Analyzing page structure...');
    
    // Check for common floor plan container patterns for Cobblestone app
    const possibleSelectors = [
      '.floor-plan',
      '.floorplan',
      '.apartment',
      '.unit',
      '.plan',
      '.listing',
      '.card',
      '[class*="floor"]',
      '[class*="plan"]',
      '[class*="apartment"]',
      '[class*="unit"]',
      '[class*="listing"]',
      '[data-testid*="floor"]',
      '[data-testid*="plan"]'
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
      
      // Try to find any elements containing price information
      const priceElements = await page.locator('text=/\\$\\d+/').all();
      console.log(`💰 Found ${priceElements.length} elements with price patterns`);
      
      if (priceElements.length > 0) {
        console.log('🔍 Attempting to extract data from price-containing elements...');
        for (let i = 0; i < Math.min(priceElements.length, 10); i++) {
          try {
            const element = priceElements[i];
            const extractedPlans = await extractFloorPlanFromElement(element, page);
            if (extractedPlans && extractedPlans.length > 0) {
              floorPlans.push(...extractedPlans);
            }
          } catch (err) {
            console.log(`❌ Error processing price element ${i + 1}:`, err);
          }
        }
      }
      
      return floorPlans;
    }
    
    console.log(`📊 Processing ${floorPlanElements.length} floor plan elements...`);
    
    // Extract data from each floor plan element
    for (let i = 0; i < floorPlanElements.length; i++) {
      try {
        const element = floorPlanElements[i];
        
        // Extract text content from the element
        const elementText = await element.textContent();
        
        console.log(`\n🔍 Processing element ${i + 1}:`);
        console.log(`Text: ${elementText?.substring(0, 200)}...`);
        
        // Try to extract floor plan information
        const extractedPlans = await extractFloorPlanFromElement(element, page);
        
        if (extractedPlans && extractedPlans.length > 0) {
          floorPlans.push(...extractedPlans);
          console.log(`✅ Successfully extracted ${extractedPlans.length} plans from element`);
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

async function extractFloorPlanFromElement(element: any, page: any): Promise<any[]> {
  try {
    // Get all text content from the element
    const textContent = await element.textContent() || '';
    
    console.log('🔍 Drift data content preview:', textContent.substring(0, 500));
    
    // The Cobblestone app appears to have all floor plans in one element
    // Let's try to parse multiple floor plans from the text
    const floorPlans: any[] = [];
    
    // Look for patterns like "A211$1,423" or "B1 - Prestige Renovation22$1,788"
    const floorPlanPattern = /(A\d+(?:\s*-\s*Prestige\s*Renovation)?\d*\d*\$[\d,]+|B\d+(?:\s*-\s*Prestige\s*Renovation)?\d*\d*\$[\d,]+)/gi;
    const matches = textContent.match(floorPlanPattern);
    
    if (matches && matches.length > 0) {
      console.log(`🏠 Found ${matches.length} potential floor plan matches in Drift data`);
      
      for (const match of matches) {
        try {
          // Extract plan name and price from each match
          const nameMatch = match.match(/^([AB]\d+(?:\s*-\s*Prestige\s*Renovation)?)/i);
          const priceMatch = match.match(/\$[\d,]+/);
          
          if (nameMatch && priceMatch) {
            let planName = nameMatch[1].trim();
            const price = priceMatch[0];
            
            // Clean up the plan name
            planName = planName.replace(/\s+/g, ' ');
            
            // Determine bedrooms and bathrooms based on plan name
            let bedrooms = 1; // Default
            let bathrooms = 1; // Default
            let sqft = 0;
            
            // Extract bedroom/bathroom info based on plan naming patterns
            if (planName.startsWith('A')) {
              bedrooms = 1;
              bathrooms = 1;
              // Set typical square footage for 1-bedroom plans
              if (planName.includes('A1')) sqft = 757;
              else if (planName.includes('A2')) sqft = 800;
              else if (planName.includes('A3')) sqft = 833;
            } else if (planName.startsWith('B')) {
              bedrooms = 2;
              bathrooms = 2;
              // Set typical square footage for 2-bedroom plans
              if (planName.includes('B1')) sqft = 1100;
              else if (planName.includes('B2')) sqft = 1200;
            }
            
            const tempFloorPlan = {
              name: planName,
              price: price,
              bedBathCount: `${bedrooms} Bed / ${bathrooms} Bath`,
              squareFootage: sqft.toString(),
              amenities: [],
              availability: 'Available'
            };
            
            floorPlans.push(tempFloorPlan);
            console.log(`✅ Extracted Drift plan: ${planName} - ${price}`);
          }
        } catch (parseError) {
          console.log(`❌ Error parsing floor plan match: ${match}`, parseError);
        }
      }
    } else {
      // Fallback: try to extract any price information
      const priceMatches = textContent.match(/\$[\d,]+/g);
      if (priceMatches && priceMatches.length > 0) {
        console.log(`💰 Found ${priceMatches.length} price patterns, creating basic floor plans`);
        
        priceMatches.forEach((price: string, index: number) => {
          const tempFloorPlan = {
            name: `Plan ${index + 1}`,
            price: price,
            bedBathCount: '? Bed / ? Bath',
            squareFootage: '0',
            amenities: [],
            availability: 'Available'
          };
          floorPlans.push(tempFloorPlan);
        });
      }
    }
    
    return floorPlans;
    
  } catch (error) {
    console.log('❌ Error extracting from Drift element:', error);
    return [];
  }
}
