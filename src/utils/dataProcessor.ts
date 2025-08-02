/**
 * Data Processing Utilities
 * Handles cleaning, formatting, and standardizing scraped apartment data
 */

import { FloorPlan, PropertySummary, DailyReport } from '../types/types';

export class DataProcessor {
  
  /**
   * Parse and clean price strings into numbers
   */
  static parsePrice(priceString: string): number {
    if (!priceString) return 0;
    
    // Remove everything except digits, commas, and periods
    const cleanPrice = priceString.replace(/[^0-9,.]/g, '');
    
    // Handle ranges like "1,583 - 1,650"
    if (cleanPrice.includes('-')) {
      const parts = cleanPrice.split('-');
      const prices = parts.map(p => parseFloat(p.replace(/,/g, '')));
      return Math.min(...prices.filter(p => !isNaN(p)));
    }
    
    // Handle "From $1,583" cases
    const matches = cleanPrice.match(/(\d+(?:,\d+)*(?:\.\d+)?)/);
    if (matches && matches[1]) {
      return parseFloat(matches[1].replace(/,/g, ''));
    }
    
    return 0;
  }

  /**
   * Parse square footage from strings
   */
  static parseSquareFootage(sqftString: string): number {
    if (!sqftString) return 0;
    
    const matches = sqftString.match(/(\d+(?:,\d+)*)/);
    if (matches && matches[1]) {
      return parseInt(matches[1].replace(/,/g, ''));
    }
    
    return 0;
  }

  /**
   * Parse bedroom count from strings
   */
  static parseBedrooms(bedroomString: string): number {
    if (!bedroomString) return 0;
    
    // Handle "Studio" cases
    if (bedroomString.toLowerCase().includes('studio')) return 0;
    
    const matches = bedroomString.match(/(\d+)\s*(beds?|bedrooms?|br)/i);
    if (matches && matches[1]) {
      return parseInt(matches[1]);
    }
    
    return 0;
  }

  /**
   * Parse bathroom count from strings (handles .5 bathrooms)
   */
  static parseBathrooms(bathroomString: string): number {
    if (!bathroomString) return 0;
    
    // Look for decimal bathrooms first (e.g., "2.5")
    const decimalMatch = bathroomString.match(/(\d+\.5)\s*(baths?|bathrooms?|ba)/i);
    if (decimalMatch && decimalMatch[1]) {
      return parseFloat(decimalMatch[1]);
    }
    
    // Look for whole number bathrooms
    const wholeMatch = bathroomString.match(/(\d+)\s*(baths?|bathrooms?|ba)/i);
    if (wholeMatch && wholeMatch[1]) {
      return parseInt(wholeMatch[1]);
    }
    
    return 0;
  }

  /**
   * Clean and format floor plan names
   */
  static cleanFloorPlanName(name: string): string {
    if (!name) return 'Unknown Plan';
    
    // Remove extra whitespace and newlines
    let cleaned = name.replace(/\s+/g, ' ').trim();
    
    // Remove redundant bedroom/bathroom info if it's already parsed separately
    cleaned = cleaned.replace(/\d+\s*(bed|bedroom|bath|bathroom|br|ba)\s*/gi, '');
    cleaned = cleaned.replace(/\d+,?\d*\s*sq\.?\s*ft\.?/gi, '');
    cleaned = cleaned.replace(/from\s*\$[\d,]+/gi, '');
    cleaned = cleaned.replace(/view\s*\d*\s*apartments?/gi, '');
    
    // Capitalize properly
    cleaned = cleaned.split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
    
    return cleaned.trim() || 'Unknown Plan';
  }

  /**
   * Determine unit type based on name and features
   */
  static determineUnitType(name: string, bathrooms: number): 'apartment' | 'townhome' | 'studio' {
    const lowerName = name.toLowerCase();
    
    if (lowerName.includes('studio')) return 'studio';
    if (lowerName.includes('townhome') || lowerName.includes('townhouse')) return 'townhome';
    if (bathrooms > 2.5) return 'townhome'; // Likely a townhome if it has 3+ bathrooms
    
    return 'apartment';
  }

  /**
   * Calculate price per square foot
   */
  static calculatePricePerSqFt(price: number, sqft: number): number {
    if (price <= 0 || sqft <= 0) return 0;
    return Math.round((price / sqft) * 100) / 100; // Round to 2 decimal places
  }

  /**
   * Standardize availability information
   */
  static standardizeAvailability(availability: string): string {
    if (!availability) return 'Contact for Availability';
    
    const lower = availability.toLowerCase();
    
    if (lower.includes('available now') || lower === 'available') {
      return 'Available Now';
    }
    
    if (lower.includes('not specified') || lower.includes('not available')) {
      return 'Contact for Availability';
    }
    
    // Try to parse dates
    const dateMatch = availability.match(/(\d{1,2}\/\d{1,2}\/\d{4})/);
    if (dateMatch) {
      return `Available ${dateMatch[1]}`;
    }
    
    return availability;
  }

  /**
   * Create property summary from floor plans
   */
  static createPropertySummary(propertyName: string, floorPlans: FloorPlan[]): PropertySummary {
    const prices = floorPlans.map(fp => fp.price).filter(p => p > 0);
    const pricesPerSqFt = floorPlans.map(fp => fp.pricePerSqFt).filter(p => p > 0);
    
    const bedroomCounts = floorPlans.reduce((acc, fp) => {
      switch (fp.bedrooms) {
        case 0: acc.studio++; break;
        case 1: acc.oneBed++; break;
        case 2: acc.twoBed++; break;
        case 3: acc.threeBed++; break;
        default: acc.fourPlusBed++; break;
      }
      return acc;
    }, { studio: 0, oneBed: 0, twoBed: 0, threeBed: 0, fourPlusBed: 0 });

    return {
      propertyName,
      totalFloorPlans: floorPlans.length,
      priceRange: {
        min: Math.min(...prices),
        max: Math.max(...prices)
      },
      avgPricePerSqFt: Math.round((pricesPerSqFt.reduce((a, b) => a + b, 0) / pricesPerSqFt.length) * 100) / 100,
      bedroomDistribution: bedroomCounts,
      availableUnits: floorPlans.filter(fp => 
        fp.availability.includes('Available') || fp.availability.includes('/')
      ).length
    };
  }

  /**
   * Create comprehensive daily report
   */
  static createDailyReport(propertySummaries: PropertySummary[], allFloorPlans: FloorPlan[]): DailyReport {
    const prices = allFloorPlans.map(fp => fp.price).filter(p => p > 0);
    const pricesPerSqFt = allFloorPlans.map(fp => fp.pricePerSqFt).filter(p => p > 0);
    
    const cheapest = allFloorPlans.reduce((min, fp) => 
      fp.price > 0 && (min.price === 0 || fp.price < min.price) ? fp : min
    );
    
    const mostExpensive = allFloorPlans.reduce((max, fp) => 
      fp.price > max.price ? fp : max
    );
    
    const bestValue = allFloorPlans.reduce((best, fp) => 
      fp.pricePerSqFt > 0 && (best.pricePerSqFt === 0 || fp.pricePerSqFt < best.pricePerSqFt) ? fp : best
    );

    return {
      date: new Date().toISOString().split('T')[0] || new Date().toDateString(),
      properties: propertySummaries,
      allFloorPlans,
      marketSummary: {
        totalUnits: allFloorPlans.length,
        avgRent: Math.round(prices.reduce((a, b) => a + b, 0) / prices.length),
        avgPricePerSqFt: Math.round((pricesPerSqFt.reduce((a, b) => a + b, 0) / pricesPerSqFt.length) * 100) / 100,
        cheapestUnit: cheapest,
        mostExpensiveUnit: mostExpensive,
        bestValueUnit: bestValue
      }
    };
  }
}
