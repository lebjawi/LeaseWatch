"""
Enhanced Type definitions for LeaseWatch application
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class PriceRange(BaseModel):
    min: float
    max: float


class FloorPlan(BaseModel):
    name: str
    price: float
    price_range: Optional[PriceRange] = None
    bedrooms: int
    bathrooms: float
    square_footage: int
    price_per_sq_ft: float
    amenities: List[str]
    availability: str
    move_in_date: Optional[str] = None
    property_name: str
    property_url: str
    description: Optional[str] = None
    unit_type: Optional[Literal['apartment', 'townhome', 'studio']] = 'apartment'


class ScrapingResult(BaseModel):
    success: bool
    message: str
    timestamp: str
    source: str
    floor_plans: List[FloorPlan]
    errors: List[str]


class BedroomDistribution(BaseModel):
    studio: int = 0
    one_bed: int = 0
    two_bed: int = 0
    three_bed: int = 0
    four_plus_bed: int = 0


class PropertySummary(BaseModel):
    property_name: str
    total_floor_plans: int
    price_range: PriceRange
    avg_price_per_sq_ft: float
    bedroom_distribution: BedroomDistribution
    available_units: int


class DailyReport(BaseModel):
    date: str
    total_properties: int
    total_floor_plans: int
    overall_price_range: PriceRange
    property_summaries: List[PropertySummary]
    scraping_results: List[ScrapingResult]
    generation_timestamp: str
    report_id: str


class ReportMetrics(BaseModel):
    total_floor_plans: int
    avg_price: float
    avg_price_per_sq_ft: float
    most_expensive_unit: Optional[FloorPlan]
    cheapest_unit: Optional[FloorPlan]
    bedroom_breakdown: BedroomDistribution
