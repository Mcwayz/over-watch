"""
Distance calculation utility module
Uses Haversine formula for calculating distance between coordinates
"""

import math
from decimal import Decimal


class DistanceCalculator:
    """Calculate distance between coordinates"""
    
    EARTH_RADIUS_KM = 6371.0
    
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        
        Args:
            lat1, lon1: Latitude and longitude of first point
            lat2, lon2: Latitude and longitude of second point
            
        Returns:
            Distance in kilometers
        """
        # Convert decimal degrees to radians
        lat1_rad = math.radians(float(lat1))
        lon1_rad = math.radians(float(lon1))
        lat2_rad = math.radians(float(lat2))
        lon2_rad = math.radians(float(lon2))
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        distance = DistanceCalculator.EARTH_RADIUS_KM * c
        return round(distance, 2)
    
    @staticmethod
    def calculate_distance_from_addresses(address1_lat, address1_lon, address2_lat, address2_lon):
        """
        Calculate distance between two addresses using their coordinates
        
        Args:
            address1_lat, address1_lon: Coordinates of first address
            address2_lat, address2_lon: Coordinates of second address
            
        Returns:
            Distance in kilometers
        """
        if not all([address1_lat, address1_lon, address2_lat, address2_lon]):
            return None
            
        try:
            return DistanceCalculator.haversine_distance(
                address1_lat, address1_lon,
                address2_lat, address2_lon
            )
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def estimate_distance(city1, city2):
        """
        Estimate distance between two cities (rough estimate based on city names)
        This is a fallback when coordinates are not available
        
        Args:
            city1: Name of first city
            city2: Name of second city
            
        Returns:
            Estimated distance in kilometers (rough estimate)
        """
        # This is a placeholder - in production, you'd use a mapping API
        # or database of city coordinates
        return None
    
    @staticmethod
    def get_delivery_tier(distance_km):
        """
        Get delivery price tier based on distance
        
        Args:
            distance_km: Distance in kilometers
            
        Returns:
            Dictionary with tier information
        """
        if distance_km is None:
            return {'tier': 'unknown', 'fee': 0, 'description': 'Distance not calculated'}
        
        tiers = [
            {'max_km': 50, 'tier': 'local', 'fee': 200, 'description': 'Local delivery'},
            {'max_km': 100, 'tier': 'short', 'fee': 400, 'description': 'Short distance'},
            {'max_km': 200, 'tier': 'medium', 'fee': 600, 'description': 'Medium distance'},
            {'max_km': 500, 'tier': 'long', 'fee': 1000, 'description': 'Long distance'},
            {'max_km': float('inf'), 'tier': 'express', 'fee': 1500, 'description': 'Express delivery'},
        ]
        
        for tier in tiers:
            if distance_km <= tier['max_km']:
                return tier
        
        return tiers[-1]


def calculate_pickup_distance(customer_lat, customer_lon, branch_lat, branch_lon):
    """
    Calculate distance from customer location to branch for pickup fee
    
    Args:
        customer_lat: Customer latitude
        customer_lon: Customer longitude
        branch_lat: Branch latitude
        branch_lon: Branch longitude
        
    Returns:
        Distance in kilometers
    """
    return DistanceCalculator.calculate_distance_from_addresses(
        customer_lat, customer_lon,
        branch_lat, branch_lon
    )


def calculate_delivery_distance(origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Calculate distance from origin to destination for delivery
    
    Args:
        origin_lat: Origin latitude
        origin_lon: Origin longitude
        dest_lat: Destination latitude
        dest_lon: Destination longitude
        
    Returns:
        Distance in kilometers
    """
    return DistanceCalculator.calculate_distance_from_addresses(
        origin_lat, origin_lon,
        dest_lat, dest_lon
    )

