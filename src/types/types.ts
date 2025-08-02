/**
 * Enhanced Type definitions for LeaseWatch application
 */

export interface FloorPlan {
  name: string;
  price: number;
  priceRange?: {
    min: number;
    max: number;
  };
  bedrooms: number;
  bathrooms: number;
  squareFootage: number;
  pricePerSqFt: number;
  amenities: string[];
  availability: string;
  moveInDate?: string;
  propertyName: string;
  propertyUrl: string;
  description?: string;
  unitType?: 'apartment' | 'townhome' | 'studio';
}

export interface ScrapingResult {
  success: boolean;
  message: string;
  timestamp: string;
  source: string;
  floorPlans: FloorPlan[];
  errors: string[];
}

export interface PropertySummary {
  propertyName: string;
  totalFloorPlans: number;
  priceRange: {
    min: number;
    max: number;
  };
  avgPricePerSqFt: number;
  bedroomDistribution: {
    studio: number;
    oneBed: number;
    twoBed: number;
    threeBed: number;
    fourPlusBed: number;
  };
  availableUnits: number;
}

export interface DailyReport {
  date: string;
  properties: PropertySummary[];
  allFloorPlans: FloorPlan[];
  marketSummary: {
    totalUnits: number;
    avgRent: number;
    avgPricePerSqFt: number;
    cheapestUnit: FloorPlan;
    mostExpensiveUnit: FloorPlan;
    bestValueUnit: FloorPlan; // Lowest price per sq ft
  };
}

export interface ScraperConfig {
  headless: boolean;
  timeout: number;
  retries: number;
  userAgent?: string;
}
