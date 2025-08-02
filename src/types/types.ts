/**
 * Type definitions for LeaseWatch application
 */

export interface FloorPlan {
  name: string;
  price: string;
  bedBathCount: string;
  squareFootage: string;
  amenities: string[];
  availability?: string;
}

export interface ApartmentUnit {
  name: string;
  beds: string;
  baths: string;
  price: string;
  availability?: string;
  squareFootage?: string;
  floorPlan?: string;
}

export interface ScrapingResult {
  success: boolean;
  message: string;
  data: ApartmentUnit[];
  timestamp: string;
  source: string;
}

export interface CamdenUnit extends ApartmentUnit {
  unitType: string;
  moveInDate?: string;
}

export interface PerimeterUnit extends ApartmentUnit {
  buildingName?: string;
  unitNumber?: string;
}

export interface DailyReport {
  date: string;
  camdenData: CamdenUnit[];
  perimeterData: PerimeterUnit[];
  summary: {
    totalUnits: number;
    avgPrice1Bed: string;
    avgPrice2Bed: string;
  };
}

export interface ScraperConfig {
  headless: boolean;
  timeout: number;
  retries: number;
  userAgent?: string;
}
