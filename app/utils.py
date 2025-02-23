from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from app.exceptions import GeocodeError


def geocode_address(address):
    """
    Geocode an address using Nominatim.

    Args:
        address: Address object with street, city, and postcode attributes

    Returns:
        tuple: (latitude, longitude)

    Raises:
        GeocodeError: If geocoding fails
    """
    try:
        geolocator = Nominatim(user_agent="maison_property_api")

        # Format address string (on one line)
        address_str = (
            f"{address.house_number} {address.street}, "
            f"{address.city}, {address.postcode}"
        )

        # Get location
        location = geolocator.geocode(address_str)

        if location is None:
            raise GeocodeError(f"Could not geocode address: {address_str}")

        return location.latitude, location.longitude

    except (GeocoderTimedOut, GeocoderServiceError) as e:
        raise GeocodeError(f"Geocoding service error: {str(e)}")
    except Exception as e:
        raise GeocodeError(f"Unexpected error during geocoding: {str(e)}")
