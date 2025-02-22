class PropertyAPIError(Exception):
    """Base exception for Property API"""

    pass


class GeocodeError(PropertyAPIError):
    """Raised when geocoding fails"""

    pass


class UserNotFoundError(PropertyAPIError):
    """Raised when referenced user doesn't exist"""

    pass


class ValidationError(PropertyAPIError):
    """Raised for data validation errors"""

    pass
