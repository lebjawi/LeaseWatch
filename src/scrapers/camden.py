"""
Camden Dunwoody Scraper
Handles scraping apartment data from Camden Living website
"""

import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from ..types.types import FloorPlan
from ..utils.data_processor import DataProcessor
from ..utils.logger import Logger

logger = Logger("CamdenScraper", quiet=True)


async def scrape_camden() -> List[FloorPlan]:
    """Main function to scrape Camden Dunwoody apartment data"""
    logger.scraping_start("Camden Dunwoody")
    
    browser = None
    
    try:
        async with async_playwright() as p:
            logger.browser_launch("Camden")
            browser = await p.chromium.launch(headless=True)
            
            page = await browser.new_page()
            
            # Set user agent to avoid detection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            url = 'https://www.camdenliving.com/apartments/dunwoody-ga/camden-dunwoody/available-apartments'
            logger.page_navigation(url)
            
            # Navigate to Camden Dunwoody apartments page
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            
            # Wait a bit for dynamic content to load
            await page.wait_for_timeout(3000)
            
            # Get and log the page title
            title = await page.title()
            logger.page_loaded(title)
            
            # Check if page has expected content
            current_url = page.url
            logger.info(f"📍 Current URL: {current_url}")
            
            # Extract floor plan data
            logger.data_extraction()
            floor_plans = await extract_camden_floor_plans(page)
            
            logger.scraping_complete("Camden Dunwoody", len(floor_plans))
            return floor_plans
    
    except Exception as error:
        error_msg = str(error) if error else "Unknown error"
        logger.scraping_error("Camden Dunwoody", error_msg)
        return []
    
    finally:
        if browser:
            await browser.close()
            logger.browser_close("Camden")


async def extract_camden_floor_plans(page: Page) -> List[FloorPlan]:
    """Extract floor plan data from Camden page"""
    try:
        # Wait for floor plan cards to load
        await page.wait_for_selector('.floorplan-card, [class*="floorplan-card"]', timeout=10000)
        
        # First, try to navigate to amenities section to get community amenities
        community_amenities: List[str] = []
        try:
            amenities_link = await page.query_selector('#community-navigation-amenities-camden-dunwoody, a[href="#amenities"]')
            if amenities_link:
                logger.info('📍 Found amenities navigation, clicking to load amenities section...')
                await amenities_link.click()
                await page.wait_for_timeout(2000)  # Wait for amenities to load
                
                # Extract community amenities
                community_amenities = await page.evaluate("""
                    () => {
                        const amenitiesSection = document.querySelector('#amenities, [id*="amenities"]');
                        const amenities = [];
                        
                        if (amenitiesSection) {
                            // Look for amenity lists in the amenities section
                            const amenityElements = amenitiesSection.querySelectorAll('li, .amenity, [class*="amenity"], .feature, [class*="feature"]');
                            amenityElements.forEach((el) => {
                                const text = el.textContent?.trim();
                                if (text && text.length > 2 && text.length < 100 && !text.includes('Amenities')) {
                                    amenities.push(text);
                                }
                            });
                        }
                        
                        return amenities;
                    }
                """)
                
                logger.info(f'✅ Extracted {len(community_amenities)} community amenities')
        
        except Exception as e:
            logger.warning(f'⚠️ Could not extract amenities: {str(e)}')
        
        # Navigate back to floor plans if we went to amenities
        try:
            floor_plans_link = await page.query_selector('a[href*="floor-plans"], a[href*="available-apartments"]')
            if floor_plans_link:
                await floor_plans_link.click()
                await page.wait_for_timeout(2000)
        except Exception:
            # If navigation fails, reload the main page
            await page.goto('https://www.camdenliving.com/apartments/dunwoody-ga/camden-dunwoody/available-apartments', 
                          wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
        
        logger.info('🔍 Extracting floor plan cards...')
        
        # Extract floor plan data using page.evaluate
        floor_plans_data = await page.evaluate("""
            () => {
                const floorPlanCards = document.querySelectorAll('.floorplan-card, [class*="floorplan"], .unit-card, [class*="unit"], .apartment-card, [class*="apartment"]');
                const results = [];
                
                floorPlanCards.forEach((card, index) => {
                    try {
                        // Extract name
                        const nameElement = card.querySelector('.floorplan-name, [class*="name"], .unit-name, .plan-name, h3, h4, .title');
                        const name = nameElement ? nameElement.textContent.trim() : `Camden Plan ${index + 1}`;
                        
                        // Extract price
                        const priceElement = card.querySelector('.price, [class*="price"], .rent, [class*="rent"], .cost');
                        const priceText = priceElement ? priceElement.textContent.trim() : '';
                        
                        // Extract bedrooms
                        const bedroomElement = card.querySelector('[class*="bed"], .bedrooms, .bed-count');
                        const bedroomText = bedroomElement ? bedroomElement.textContent.trim() : '';
                        
                        // Extract bathrooms
                        const bathroomElement = card.querySelector('[class*="bath"], .bathrooms, .bath-count');
                        const bathroomText = bathroomElement ? bathroomElement.textContent.trim() : '';
                        
                        // Extract square footage
                        const sqftElement = card.querySelector('[class*="sqft"], [class*="square"], .size, .area');
                        const sqftText = sqftElement ? sqftElement.textContent.trim() : '';
                        
                        // Extract availability
                        const availabilityElement = card.querySelector('.availability, [class*="available"], .status, [class*="status"]');
                        const availabilityText = availabilityElement ? availabilityElement.textContent.trim() : 'Available';
                        
                        // Extract amenities from this specific unit
                        const amenityElements = card.querySelectorAll('.amenity, [class*="amenity"], .feature, [class*="feature"], li');
                        const unitAmenities = [];
                        amenityElements.forEach(el => {
                            const text = el.textContent?.trim();
                            if (text && text.length > 2 && text.length < 50) {
                                unitAmenities.push(text);
                            }
                        });
                        
                        // Only add if we have at least a name and some pricing info
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
                        console.log('Error processing floor plan card:', error);
                    }
                });
                
                return results;
            }
        """)
        
        logger.info(f'📊 Found {len(floor_plans_data)} potential floor plan cards')
        
        if not floor_plans_data:
            logger.warning('⚠️ No floor plan cards found, trying alternative selectors...')
            
            # Try alternative extraction method
            floor_plans_data = await page.evaluate("""
                () => {
                    // Try to find any elements that might contain apartment data
                    const potentialCards = document.querySelectorAll('div[class*="unit"], div[class*="plan"], div[class*="apartment"], .property-card, .listing-card');
                    const results = [];
                    
                    potentialCards.forEach((card, index) => {
                        const allText = card.textContent || '';
                        // Look for patterns that suggest this is an apartment listing
                        if (allText.includes('$') && (allText.includes('bed') || allText.includes('bath') || allText.includes('sqft') || allText.includes('sq ft'))) {
                            results.push({
                                name: `Camden Unit ${index + 1}`,
                                priceText: allText,
                                bedroomText: allText,
                                bathroomText: allText,
                                sqftText: allText,
                                availabilityText: 'Available',
                                unitAmenities: []
                            });
                        }
                    });
                    
                    return results;
                }
            """)
            
            logger.info(f'🔄 Alternative extraction found {len(floor_plans_data)} potential units')
        
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
                
                # Combine community and unit amenities
                all_amenities = community_amenities + data['unitAmenities']
                cleaned_amenities = DataProcessor.clean_amenities(all_amenities)
                
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
                    property_name="Camden Dunwoody",
                    property_url="https://www.camdenliving.com/apartments/dunwoody-ga/camden-dunwoody",
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
        
        logger.info(f'✅ Successfully processed {len(floor_plans)} valid floor plans')
        return floor_plans
    
    except Exception as error:
        logger.error(f'❌ Error extracting Camden floor plans: {str(error)}')
        return []
