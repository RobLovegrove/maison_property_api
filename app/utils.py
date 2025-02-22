from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from app.exceptions import GeocodeError
from typing import Tuple, Optional
import time


def geocode_address(
    house_number: str,
    street: str,
    city: str,
    postcode: str,
    country: str = "UK",
    max_retries: int = 3,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Convert address to latitude and longitude with retries.
    Returns (latitude, longitude) or raises GeocodeError.
    """
    for attempt in range(max_retries):
        try:
            geolocator = Nominatim(user_agent="maison_property_api")
            address = f"{house_number} {street}, {city}, {postcode}, {country}"

            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude

            # Try without house number if first attempt fails
            address = f"{street}, {city}, {postcode}, {country}"
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude

            raise GeocodeError(f"Could not geocode address: {address}")

        except GeocoderTimedOut:
            if attempt == max_retries - 1:
                raise GeocodeError("Geocoding service timed out")
            time.sleep(1)  # Wait before retry

        except GeocoderServiceError as e:
            raise GeocodeError(f"Geocoding service error: {str(e)}")

    return None, None
