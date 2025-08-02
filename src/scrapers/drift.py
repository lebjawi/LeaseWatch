"""
Drift Dunwoody Scraper
Handles scraping apartment data from Drift Dunwoody website
"""

import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from ..types.types import FloorPlan
from ..utils.data_processor import DataProcessor
from ..utils.logger import Logger

logger = Logger("DriftScraper")


async def scrape_drift() -> List[FloorPlan]:
    """Main function to scrape Drift Dunwoody apartment data"""
    logger.scraping_start("Drift Dunwoody")
    
    browser = None
    
    try:
        async with async_playwright() as p:
            logger.browser_launch("Drift")
            browser = await p.chromium.launch(headless=True)
            
            page = await browser.new_page()
            
            # Set user agent to avoid detection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            })
            
            url = 'https://app.getcobblestone.com/complex/2oRUqV2UXteJYr25ds4syVrY5Ap/floorplans'
            logger.page_navigation(url)
            
            # Navigate directly to the Cobblestone floor plans page
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for page to be fully loaded
            await page.wait_for_timeout(5000)
            
            # Get and log the page title
            title = await page.title()
            logger.page_loaded(title)
            
            # Check if page has expected content
            current_url = page.url
            logger.info(f"📍 Current URL: {current_url}")
            
            # Extract floor plan data
            logger.data_extraction()
            floor_plans = await extract_drift_floor_plans(page)
            
            logger.scraping_complete("Drift Dunwoody", len(floor_plans))
            return floor_plans
    
    except Exception as error:
        error_msg = str(error) if error else "Unknown error"
        logger.scraping_error("Drift Dunwoody", error_msg)
        return []
    
    finally:
        if browser:
            await browser.close()
            logger.browser_close("Drift")


async def extract_drift_floor_plans(page: Page) -> List[FloorPlan]:
    """Extract floor plan data from Drift Dunwoody page"""
    try:
        # Wait for floor plan content to load - Cobblestone app specific selectors
        logger.info('⏳ Waiting for Drift floor plans to load...')
        
        # Try multiple selectors as the app might use different ones
        selectors_to_try = [
            '.floor-plan-card',
            '[data-testid*="floorplan"]',
            '[class*="floorplan"]',
            '.unit-card',
            '[class*="unit"]',
            '.apartment-card',
            '[class*="apartment"]',
            '.plan-card',
            '[class*="plan"]'
        ]
        
        floor_plan_selector = None
        for selector in selectors_to_try:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                floor_plan_selector = selector
                logger.info(f'✅ Found floor plans using selector: {selector}')
                break
            except Exception:
                continue
        
        if not floor_plan_selector:
            logger.warning('⚠️ No standard floor plan selectors found, trying generic approach...')
        
        # Extra wait for dynamic content
        await page.wait_for_timeout(3000)
        
        logger.info('🔍 Extracting Drift floor plan data...')
        
        # Extract floor plan data using page.evaluate
        floor_plans_data = await page.evaluate("""
            () => {
                // Try multiple selectors for Cobblestone app
                const possibleSelectors = [
                    '.floor-plan-card',
                    '[data-testid*="floorplan"]',
                    '[class*="floorplan"]',
                    '.unit-card',
                    '[class*="unit"]',
                    '.apartment-card',
                    '[class*="apartment"]',
                    '.plan-card',
                    '[class*="plan"]',
                    '.property-card',
                    '[class*="property"]'
                ];
                
                let floorPlanCards = [];
                
                // Try each selector until we find cards
                for (const selector of possibleSelectors) {
                    floorPlanCards = document.querySelectorAll(selector);
                    if (floorPlanCards.length > 0) {
                        console.log(`Found ${floorPlanCards.length} cards with selector: ${selector}`);
                        break;
                    }
                }
                
                // If still no cards found, try to find any div that might contain apartment data
                if (floorPlanCards.length === 0) {
                    const allDivs = document.querySelectorAll('div');
                    floorPlanCards = Array.from(allDivs).filter(div => {
                        const text = div.textContent || '';
                        return text.includes('$') && (text.includes('bed') || text.includes('bath') || text.includes('sqft') || text.includes('sq ft'));
                    });
                    console.log(`Found ${floorPlanCards.length} potential cards using text matching`);
                }
                
                const results = [];
                
                floorPlanCards.forEach((card, index) => {
                    try {
                        // Extract name - try multiple approaches
                        let name = '';
                        const nameSelectors = [
                            '.floor-plan-name',
                            '.plan-name',
                            '.unit-name',
                            '.apartment-name',
                            '[data-testid*="name"]',
                            'h1', 'h2', 'h3', 'h4', 'h5',
                            '.title',
                            '[class*="title"]',
                            '[class*="name"]'
                        ];
                        
                        for (const selector of nameSelectors) {
                            const nameElement = card.querySelector(selector);
                            if (nameElement && nameElement.textContent.trim()) {
                                name = nameElement.textContent.trim();
                                break;
                            }
                        }
                        
                        if (!name) {
                            name = `Drift Plan ${index + 1}`;
                        }
                        
                        // Extract price
                        let priceText = '';
                        const priceSelectors = [
                            '.price',
                            '.rent',
                            '.cost',
                            '[class*="price"]',
                            '[class*="rent"]',
                            '[class*="cost"]',
                            '[data-testid*="price"]',
                            '[data-testid*="rent"]'
                        ];
                        
                        for (const selector of priceSelectors) {
                            const priceElement = card.querySelector(selector);
                            if (priceElement && priceElement.textContent.includes('$')) {
                                priceText = priceElement.textContent.trim();
                                break;
                            }
                        }
                        
                        // If no specific price element, look for $ in any text
                        if (!priceText) {
                            const allText = card.textContent || '';
                            const priceMatch = allText.match(/\\$[\\d,]+/);
                            if (priceMatch) {
                                priceText = priceMatch[0];
                            }
                        }
                        
                        // Extract bedrooms
                        let bedroomText = '';
                        const bedSelectors = [
                            '.bedrooms',
                            '.bed-count',
                            '[class*="bed"]',
                            '[data-testid*="bed"]'
                        ];
                        
                        for (const selector of bedSelectors) {
                            const bedElement = card.querySelector(selector);
                            if (bedElement) {
                                bedroomText = bedElement.textContent.trim();
                                break;
                            }
                        }
                        
                        // If no specific bedroom element, look for bedroom info in text
                        if (!bedroomText) {
                            const allText = card.textContent || '';
                            const bedMatch = allText.match(/(\\d+)\\s*bed|studio/i);
                            if (bedMatch) {
                                bedroomText = bedMatch[0];
                            }
                        }
                        
                        // Extract bathrooms
                        let bathroomText = '';
                        const bathSelectors = [
                            '.bathrooms',
                            '.bath-count',
                            '[class*="bath"]',
                            '[data-testid*="bath"]'
                        ];
                        
                        for (const selector of bathSelectors) {
                            const bathElement = card.querySelector(selector);
                            if (bathElement) {
                                bathroomText = bathElement.textContent.trim();
                                break;
                            }
                        }
                        
                        // If no specific bathroom element, look for bathroom info in text
                        if (!bathroomText) {
                            const allText = card.textContent || '';
                            const bathMatch = allText.match(/(\\d+(?:\\.5)?)\\s*bath/i);
                            if (bathMatch) {
                                bathroomText = bathMatch[0];
                            } else {
                                bathroomText = '1 bath'; // Default assumption
                            }
                        }
                        
                        // Extract square footage
                        let sqftText = '';
                        const sqftSelectors = [
                            '.square-footage',
                            '.sqft',
                            '.size',
                            '.area',
                            '[class*="sqft"]',
                            '[class*="square"]',
                            '[data-testid*="sqft"]',
                            '[data-testid*="square"]'
                        ];
                        
                        for (const selector of sqftSelectors) {
                            const sqftElement = card.querySelector(selector);
                            if (sqftElement) {
                                sqftText = sqftElement.textContent.trim();
                                break;
                            }
                        }
                        
                        // If no specific sqft element, look for sqft info in text
                        if (!sqftText) {
                            const allText = card.textContent || '';
                            const sqftMatch = allText.match(/(\\d+(?:,\\d+)*)\\s*(?:sq\\s*ft|sqft)/i);
                            if (sqftMatch) {
                                sqftText = sqftMatch[0];
                            }
                        }
                        
                        // Extract availability
                        let availabilityText = 'Available';
                        const availabilitySelectors = [
                            '.availability',
                            '.status',
                            '[class*="available"]',
                            '[class*="status"]',
                            '[data-testid*="available"]',
                            '[data-testid*="status"]'
                        ];
                        
                        for (const selector of availabilitySelectors) {
                            const availElement = card.querySelector(selector);
                            if (availElement) {
                                availabilityText = availElement.textContent.trim();
                                break;
                            }
                        }
                        
                        // Extract amenities
                        const amenityElements = card.querySelectorAll('.amenity, [class*="amenity"], .feature, [class*="feature"], li');
                        const unitAmenities = [];
                        amenityElements.forEach(el => {
                            const text = el.textContent?.trim();
                            if (text && text.length > 2 && text.length < 50 && !text.includes('$')) {
                                unitAmenities.push(text);
                            }
                        });
                        
                        // Only add if we have meaningful data
                        if (name && (priceText || bedroomText || sqftText)) {
                            results.push({
                                name: name,
                                priceText: priceText,
                                bedroomText: bedroomText,
                                bathroomText: bathroomText,
                                sqftText: sqftText,
                                availabilityText: availabilityText,
                                unitAmenities: unitAmenities
                            });
                        }
                    } catch (error) {
                        console.log('Error processing Drift floor plan card:', error);
                    }
                });
                
                return results;
            }
        """)
        
        logger.info(f'📊 Found {len(floor_plans_data)} potential Drift floor plan cards')
        
        # If we still don't have data, try a more aggressive approach
        if not floor_plans_data:
            logger.warning('⚠️ No floor plan data found with standard approach, trying alternative method...')
            
            # Get all text content and try to parse apartment listings from it
            page_content = await page.evaluate("""
                () => {
                    return document.body.textContent || '';
                }
            """)
            
            # Look for patterns that suggest apartment listings
            import re
            apartment_patterns = re.findall(r'(\$[\d,]+).*?(\d+)\s*bed.*?(\d+(?:\.\d+)?)\s*bath.*?(\d+(?:,\d+)*)\s*(?:sq\s*ft|sqft)', page_content, re.IGNORECASE)
            
            for i, match in enumerate(apartment_patterns):
                floor_plans_data.append({
                    'name': f'Drift Unit {i + 1}',
                    'priceText': match[0],
                    'bedroomText': f'{match[1]} bed',
                    'bathroomText': f'{match[2]} bath',
                    'sqftText': f'{match[3]} sq ft',
                    'availabilityText': 'Available',
                    'unitAmenities': []
                })
            
            logger.info(f'🔄 Alternative extraction found {len(apartment_patterns)} potential units')
        
        # Process the extracted data
        floor_plans: List[FloorPlan] = []
        
        for data in floor_plans_data:
            try:
                # Parse the extracted data
                price = DataProcessor.parse_price(data['priceText'])
                bedrooms = DataProcessor.parse_bedroom_count(data['bedroomText'])
                bathrooms = DataProcessor.parse_bathroom_count(data['bathroomText'])
                square_footage = DataProcessor.parse_square_footage(data['sqftText'])
                
                # Skip if we couldn't extract meaningful data
                if price <= 0 and square_footage <= 0:
                    continue
                
                # Calculate price per sq ft
                price_per_sq_ft = DataProcessor.calculate_price_per_sqft(price, square_footage)
                
                # Clean amenities
                cleaned_amenities = DataProcessor.clean_amenities(data['unitAmenities'])
                
                # Standardize availability
                availability = DataProcessor.standardize_availability(data['availabilityText'])
                
                # Create FloorPlan object
                floor_plan = FloorPlan(
                    name=data['name'],
                    price=price,
                    bedrooms=bedrooms,
                    bathrooms=bathrooms,
                    square_footage=square_footage,
                    price_per_sq_ft=price_per_sq_ft,
                    amenities=cleaned_amenities,
                    availability=availability,
                    property_name="Drift Dunwoody",
                    property_url="https://app.getcobblestone.com/complex/2oRUqV2UXteJYr25ds4syVrY5Ap/floorplans",
                    unit_type="apartment"
                )
                
                # Validate the floor plan before adding
                if DataProcessor.validate_floor_plan(floor_plan.model_dump()):
                    floor_plans.append(floor_plan)
                    logger.debug(f'✅ Added floor plan: {floor_plan.name} - ${floor_plan.price}')
                else:
                    logger.debug(f'❌ Skipped invalid floor plan: {data["name"]}')
            
            except Exception as e:
                logger.warning(f'⚠️ Error processing floor plan data: {str(e)}')
                continue
        
        logger.info(f'✅ Successfully processed {len(floor_plans)} valid Drift floor plans')
        return floor_plans
    
    except Exception as error:
        logger.error(f'❌ Error extracting Drift floor plans: {str(error)}')
        return []
