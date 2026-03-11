"""
Pricing calculation utility module
"""
from decimal import Decimal


class PricingEngine:
    """Pricing calculation engine"""

    # Pricing constants
    BASE_FEE = Decimal('500.00')  # Base fee in currency
    RATE_PER_KG = Decimal('50.00')  # Per kilogram rate
    INSURANCE_RATE = Decimal('0.01')  # 1% of declared value
    
    # Pickup fee constants
    PICKUP_BASE_FEE = Decimal('200.00')  # Base pickup fee
    PICKUP_RATE_PER_KM = Decimal('15.00')  # Rate per kilometer for pickup
    PRIORITY_FEE = Decimal('100.00')  # Additional fee for priority pickup

    # Distance-based pricing tiers
    DISTANCE_TIERS = [
        {'max_km': 50, 'fee': Decimal('200.00')},
        {'max_km': 100, 'fee': Decimal('400.00')},
        {'max_km': 200, 'fee': Decimal('600.00')},
        {'max_km': 500, 'fee': Decimal('1000.00')},
        {'max_km': float('inf'), 'fee': Decimal('1500.00')},
    ]

    @staticmethod
    def calculate_distance_fee(distance_km):
        """Calculate distance-based fee"""
        distance = Decimal(str(distance_km))
        for tier in PricingEngine.DISTANCE_TIERS:
            if distance <= tier['max_km']:
                return tier['fee']
        return PricingEngine.DISTANCE_TIERS[-1]['fee']

    @staticmethod
    def calculate_insurance_fee(declared_value):
        """Calculate 1% insurance fee"""
        value = Decimal(str(declared_value))
        return value * PricingEngine.INSURANCE_RATE

    @staticmethod
    def calculate_delivery_price(weight_kg, distance_km, declared_value):
        """
        Calculate total delivery price
        PRICE = Base Fee + (Weight × Rate per KG) + Distance Fee + Insurance Fee
        """
        weight = Decimal(str(weight_kg))
        distance = Decimal(str(distance_km))
        value = Decimal(str(declared_value))

        base_fee = PricingEngine.BASE_FEE
        weight_fee = weight * PricingEngine.RATE_PER_KG
        distance_fee = PricingEngine.calculate_distance_fee(distance)
        insurance_fee = PricingEngine.calculate_insurance_fee(value)

        total_price = base_fee + weight_fee + distance_fee + insurance_fee

        return {
            'base_fee': base_fee,
            'weight_fee': weight_fee,
            'distance_fee': distance_fee,
            'insurance_fee': insurance_fee,
            'total_price': total_price,
        }

    @staticmethod
    def calculate_pickup_fee(distance_km, is_priority=False):
        """
        Calculate pickup fee
        PICKUP FEE = Base Fee + (Distance × Rate per KM) + Priority Fee
        
        Args:
            distance_km: Distance from pickup location to branch in kilometers
            is_priority: Whether this is a priority pickup request
        """
        distance = Decimal(str(distance_km))
        
        base_fee = PricingEngine.PICKUP_BASE_FEE
        distance_fee = distance * PricingEngine.PICKUP_RATE_PER_KM
        priority_fee = PricingEngine.PRIORITY_FEE if is_priority else Decimal('0')
        
        total_pickup_fee = base_fee + distance_fee + priority_fee
        
        return {
            'base_fee': base_fee,
            'distance_fee': distance_fee,
            'distance_km': distance_km,
            'priority_fee': priority_fee,
            'is_priority': is_priority,
            'total_pickup_fee': total_pickup_fee,
        }

    @staticmethod
    def calculate_total_price(delivery_price, pickup_fee=0):
        """
        Calculate total price including delivery and pickup fees
        
        Args:
            delivery_price: The calculated delivery price
            pickup_fee: The pickup fee (0 for branch drop-off)
        """
        delivery = Decimal(str(delivery_price))
        pickup = Decimal(str(pickup_fee))
        
        return {
            'delivery_price': delivery,
            'pickup_fee': pickup,
            'total_price': delivery + pickup,
        }

    @staticmethod
    def get_pricing_breakdown(weight_kg, distance_km, declared_value):
        """Get detailed pricing breakdown"""
        pricing = PricingEngine.calculate_delivery_price(weight_kg, distance_km, declared_value)
        return {
            'base_fee': float(pricing['base_fee']),
            'weight_fee': float(pricing['weight_fee']),
            'distance_fee': float(pricing['distance_fee']),
            'insurance_fee': float(pricing['insurance_fee']),
            'total_price': float(pricing['total_price']),
        }
    
    @staticmethod
    def get_pickup_fee_breakdown(distance_km, is_priority=False):
        """Get detailed pickup fee breakdown"""
        pickup = PricingEngine.calculate_pickup_fee(distance_km, is_priority)
        return {
            'base_fee': float(pickup['base_fee']),
            'distance_fee': float(pickup['distance_fee']),
            'distance_km': float(pickup['distance_km']),
            'priority_fee': float(pickup['priority_fee']),
            'is_priority': pickup['is_priority'],
            'total_pickup_fee': float(pickup['total_pickup_fee']),
        }
