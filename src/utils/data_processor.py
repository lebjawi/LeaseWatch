"""
Data Processing Utilities
Handles cleaning, formatting, and standardizing scraped apartment data
"""

import re
from typing import List, Optional
from datetime import datetime, date
from ..types.types import FloorPlan, PropertySummary, DailyReport, BedroomDistribution, PriceRange


class DataProcessor:
    """
    Utility class for processing and cleaning apartment data
    """
    
    @staticmethod
    def parse_price(price_string: str) -> float:
        """Parse and clean price strings into numbers"""
        if not price_string:
            return 0.0
        
        # Handle ranges like "1,583 - 1,650" first
        if '-' in price_string:
            parts = price_string.split('-')
            prices = []
            for part in parts:
                # Extract digits and commas from each part
                clean_part = re.sub(r'[^0-9,.]', '', part.strip())
                try:
                    price = float(clean_part.replace(',', ''))
                    if price > 0:
                        prices.append(price)
                except ValueError:
                    continue
            return min(prices) if prices else 0.0
        
        # Handle "From $1,583" cases - find all numbers with commas
        matches = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', price_string)
        if matches:
            try:
                # Take the first number found
                return float(matches[0].replace(',', ''))
            except ValueError:
                pass
        
        return 0.0

    @staticmethod
    def parse_square_footage(sqft_string: str) -> int:
        """Parse square footage from strings"""
        if not sqft_string:
            return 0
        
        matches = re.search(r'(\d+(?:,\d+)*)', sqft_string)
        if matches:
            try:
                return int(matches.group(1).replace(',', ''))
            except ValueError:
                pass
        
        return 0

    @staticmethod
    def parse_bedroom_count(bedroom_string: str) -> int:
        """Parse bedroom count from strings"""
        if not bedroom_string:
            return 0
        
        bedroom_lower = bedroom_string.lower().strip()
        
        # Handle studio apartments
        if 'studio' in bedroom_lower:
            return 0
        
        # Extract number from strings like "1 Bed", "2 Bedroom", etc.
        matches = re.search(r'(\d+)', bedroom_lower)
        if matches:
            try:
                return int(matches.group(1))
            except ValueError:
                pass
        
        return 0

    @staticmethod
    def parse_bathroom_count(bathroom_string: str) -> float:
        """Parse bathroom count from strings, supports half bathrooms"""
        if not bathroom_string:
            return 0.0
        
        bathroom_lower = bathroom_string.lower().strip()
        
        # Handle half bathrooms
        if '1.5' in bathroom_lower or 'one and a half' in bathroom_lower:
            return 1.5
        elif '2.5' in bathroom_lower or 'two and a half' in bathroom_lower:
            return 2.5
        elif '3.5' in bathroom_lower or 'three and a half' in bathroom_lower:
            return 3.5
        
        # Extract number from strings like "1 Bath", "2 Bathroom", etc.
        matches = re.search(r'(\d+(?:\.\d+)?)', bathroom_lower)
        if matches:
            try:
                return float(matches.group(1))
            except ValueError:
                pass
        
        return 1.0  # Default to 1 bathroom if unclear

    @staticmethod
    def calculate_price_per_sqft(price: float, square_footage: int) -> float:
        """Calculate price per square foot"""
        if square_footage <= 0:
            return 0.0
        return round(price / square_footage, 2)

    @staticmethod
    def clean_amenities(amenities_raw: List[str]) -> List[str]:
        """Clean and standardize amenity names"""
        cleaned = []
        for amenity in amenities_raw:
            if not amenity:
                continue
            
            # Remove extra whitespace and convert to title case
            cleaned_amenity = ' '.join(amenity.strip().split())
            
            # Skip very short or very long amenities (likely not useful)
            if 2 <= len(cleaned_amenity) <= 50:
                cleaned.append(cleaned_amenity)
        
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for amenity in cleaned:
            if amenity.lower() not in seen:
                seen.add(amenity.lower())
                result.append(amenity)
        
        return result

    @staticmethod
    def standardize_availability(availability_string: str) -> str:
        """Standardize availability strings"""
        if not availability_string:
            return "Unknown"
        
        availability_lower = availability_string.lower().strip()
        
        if 'available now' in availability_lower or 'immediate' in availability_lower:
            return "Available Now"
        elif 'coming soon' in availability_lower or 'waitlist' in availability_lower:
            return "Coming Soon"
        elif 'not available' in availability_lower or 'unavailable' in availability_lower:
            return "Not Available"
        else:
            # Try to extract and format date
            date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', availability_string)
            if date_match:
                return f"Available {date_match.group(1)}"
            
            return availability_string.strip()

    @staticmethod
    def validate_floor_plan(floor_plan: dict) -> bool:
        """Validate that a floor plan has minimum required data"""
        required_fields = ['name', 'price', 'property_name']
        
        for field in required_fields:
            if field not in floor_plan or not floor_plan[field]:
                return False
        
        # Price should be reasonable (between $500 and $10,000)
        price = floor_plan.get('price', 0)
        if not (500 <= price <= 10000):
            return False
        
        return True

    @staticmethod
    def generate_property_summary(floor_plans: List[FloorPlan]) -> PropertySummary:
        """Generate summary statistics for a property"""
        if not floor_plans:
            return PropertySummary(
                property_name="Unknown",
                total_floor_plans=0,
                price_range=PriceRange(min=0, max=0),
                avg_price_per_sq_ft=0.0,
                bedroom_distribution=BedroomDistribution(),
                available_units=0
            )
        
        property_name = floor_plans[0].property_name
        prices = [fp.price for fp in floor_plans if fp.price > 0]
        price_per_sqft = [fp.price_per_sq_ft for fp in floor_plans if fp.price_per_sq_ft > 0]
        
        # Count bedroom distribution
        bedroom_dist = BedroomDistribution()
        available_count = 0
        
        for fp in floor_plans:
            if fp.availability.lower() not in ['not available', 'unavailable']:
                available_count += 1
            
            if fp.bedrooms == 0:
                bedroom_dist.studio += 1
            elif fp.bedrooms == 1:
                bedroom_dist.one_bed += 1
            elif fp.bedrooms == 2:
                bedroom_dist.two_bed += 1
            elif fp.bedrooms == 3:
                bedroom_dist.three_bed += 1
            else:
                bedroom_dist.four_plus_bed += 1
        
        return PropertySummary(
            property_name=property_name,
            total_floor_plans=len(floor_plans),
            price_range=PriceRange(
                min=min(prices) if prices else 0,
                max=max(prices) if prices else 0
            ),
            avg_price_per_sq_ft=round(sum(price_per_sqft) / len(price_per_sqft), 2) if price_per_sqft else 0.0,
            bedroom_distribution=bedroom_dist,
            available_units=available_count
        )

    @staticmethod
    def format_timestamp() -> str:
        """Generate formatted timestamp string"""
        return datetime.now().isoformat()

    @staticmethod
    def format_date() -> str:
        """Generate formatted date string"""
        return date.today().isoformat()
