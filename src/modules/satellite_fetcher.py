"""
Satellite Image Fetcher Module
Fetches satellite imagery from free API sources for change detection analysis.
"""

import os
import requests
from datetime import datetime
from typing import Optional, Tuple, Dict
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SatelliteImageFetcher:
    """Fetches satellite images from various free APIs."""

    def __init__(self):
        """Initialize the satellite image fetcher."""
        self.nasa_gibs_base = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best"
        self.sentinel_hub_base = "https://services.sentinel-hub.com/ogc/wms"

        # API keys (to be set by user)
        self.sentinel_hub_instance_id = os.getenv("SENTINEL_HUB_INSTANCE_ID")
        self.mapbox_token = os.getenv("MAPBOX_ACCESS_TOKEN")

    def fetch_nasa_gibs_image(
        self,
        latitude: float,
        longitude: float,
        date: str,
        zoom: int = 10,
        width: int = 512,
        height: int = 512
    ) -> Optional[Image.Image]:
        """
        Fetch satellite image from NASA GIBS (Global Imagery Browse Services).

        This service is completely FREE and requires NO API key!

        Args:
            latitude: Latitude of location
            longitude: Longitude of location
            date: Date in YYYY-MM-DD format
            zoom: Zoom level (1-14)
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            PIL Image object or None if failed
        """
        try:
            logger.info(f"Fetching NASA GIBS image for ({latitude}, {longitude}) on {date}")

            # Calculate tile coordinates
            # For simplicity, using a direct image request to GIBS WMS
            layer = "MODIS_Terra_CorrectedReflectance_TrueColor"

            # Calculate bounding box (approximate)
            delta = 0.5 / (2 ** zoom)  # Rough approximation
            bbox = f"{longitude-delta},{latitude-delta},{longitude+delta},{latitude+delta}"

            url = (
                f"https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?"
                f"SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&"
                f"LAYERS={layer}&"
                f"CRS=EPSG:4326&"
                f"BBOX={bbox}&"
                f"WIDTH={width}&HEIGHT={height}&"
                f"FORMAT=image/jpeg&"
                f"TIME={date}"
            )

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            image = Image.open(io.BytesIO(response.content))
            logger.info("Successfully fetched NASA GIBS image")
            return image

        except Exception as e:
            logger.error(f"Error fetching NASA GIBS image: {e}")
            return None

    def fetch_sentinel_hub_image(
        self,
        latitude: float,
        longitude: float,
        date: str,
        width: int = 512,
        height: int = 512
    ) -> Optional[Image.Image]:
        """
        Fetch satellite image from Sentinel Hub.

        Requires FREE Sentinel Hub account and instance ID.
        Sign up at: https://www.sentinel-hub.com/

        Args:
            latitude: Latitude of location
            longitude: Longitude of location
            date: Date in YYYY-MM-DD format
            width: Image width
            height: Image height

        Returns:
            PIL Image object or None if failed
        """
        if not self.sentinel_hub_instance_id:
            logger.warning("Sentinel Hub instance ID not configured")
            return None

        try:
            logger.info(f"Fetching Sentinel Hub image for ({latitude}, {longitude}) on {date}")

            # Calculate bounding box
            delta = 0.01
            bbox = f"{longitude-delta},{latitude-delta},{longitude+delta},{latitude+delta}"

            url = (
                f"{self.sentinel_hub_base}/{self.sentinel_hub_instance_id}?"
                f"SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&"
                f"LAYERS=TRUE-COLOR-S2-L1C&"
                f"BBOX={bbox}&"
                f"WIDTH={width}&HEIGHT={height}&"
                f"FORMAT=image/jpeg&"
                f"TIME={date}/{date}"
            )

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            image = Image.open(io.BytesIO(response.content))
            logger.info("Successfully fetched Sentinel Hub image")
            return image

        except Exception as e:
            logger.error(f"Error fetching Sentinel Hub image: {e}")
            return None

    def fetch_mapbox_satellite_image(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 15,
        width: int = 512,
        height: int = 512
    ) -> Optional[Image.Image]:
        """
        Fetch satellite image from Mapbox Satellite.

        Requires FREE Mapbox account and access token.
        Sign up at: https://www.mapbox.com/
        Free tier: 50,000 requests/month

        Args:
            latitude: Latitude of location
            longitude: Longitude of location
            zoom: Zoom level (1-20)
            width: Image width (max 1280)
            height: Image height (max 1280)

        Returns:
            PIL Image object or None if failed
        """
        if not self.mapbox_token:
            logger.warning("Mapbox access token not configured")
            return None

        try:
            logger.info(f"Fetching Mapbox satellite image for ({latitude}, {longitude})")

            # Mapbox Static Images API
            url = (
                f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
                f"{longitude},{latitude},{zoom}/{width}x{height}?"
                f"access_token={self.mapbox_token}"
            )

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            image = Image.open(io.BytesIO(response.content))
            logger.info("Successfully fetched Mapbox satellite image")
            return image

        except Exception as e:
            logger.error(f"Error fetching Mapbox image: {e}")
            return None

    def fetch_image_pair(
        self,
        latitude: float,
        longitude: float,
        date1: str,
        date2: str,
        source: str = "nasa",
        **kwargs
    ) -> Tuple[Optional[Image.Image], Optional[Image.Image]]:
        """
        Fetch a pair of satellite images for change detection.

        Args:
            latitude: Latitude of location
            longitude: Longitude of location
            date1: First date (before) in YYYY-MM-DD format
            date2: Second date (after) in YYYY-MM-DD format
            source: Image source ('nasa', 'sentinel', 'mapbox')
            **kwargs: Additional parameters for the specific API

        Returns:
            Tuple of (before_image, after_image)
        """
        logger.info(f"Fetching image pair from {source} for change detection")

        if source.lower() == "nasa":
            img1 = self.fetch_nasa_gibs_image(latitude, longitude, date1, **kwargs)
            img2 = self.fetch_nasa_gibs_image(latitude, longitude, date2, **kwargs)
        elif source.lower() == "sentinel":
            img1 = self.fetch_sentinel_hub_image(latitude, longitude, date1, **kwargs)
            img2 = self.fetch_sentinel_hub_image(latitude, longitude, date2, **kwargs)
        elif source.lower() == "mapbox":
            # Mapbox doesn't have temporal data, so we can only get current image
            logger.warning("Mapbox doesn't support historical imagery - fetching current only")
            img1 = None
            img2 = self.fetch_mapbox_satellite_image(latitude, longitude, **kwargs)
        else:
            logger.error(f"Unknown source: {source}")
            return None, None

        return img1, img2

    def save_image(self, image: Image.Image, filepath: str) -> bool:
        """
        Save image to file.

        Args:
            image: PIL Image object
            filepath: Path to save the image

        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            image.save(filepath, quality=95)
            logger.info(f"Image saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False


# Example locations for testing
EXAMPLE_LOCATIONS = {
    "Amazon Rainforest (Deforestation)": {
        "lat": -3.4653,
        "lon": -62.2159,
        "description": "Area showing deforestation over time"
    },
    "Dubai (Urban Development)": {
        "lat": 25.2048,
        "lon": 55.2708,
        "description": "Rapid urban development"
    },
    "Aral Sea (Water Loss)": {
        "lat": 45.0,
        "lon": 60.0,
        "description": "Dramatic water level changes"
    },
    "Las Vegas (Urban Expansion)": {
        "lat": 36.1699,
        "lon": -115.1398,
        "description": "City expansion into desert"
    },
    "Jakarta Bay (Land Reclamation)": {
        "lat": -6.1751,
        "lon": 106.8650,
        "description": "Coastal land reclamation"
    }
}


def test_fetcher():
    """Test the satellite image fetcher."""
    fetcher = SatelliteImageFetcher()

    # Test NASA GIBS (no API key needed!)
    print("Testing NASA GIBS API...")
    location = EXAMPLE_LOCATIONS["Dubai (Urban Development)"]

    image = fetcher.fetch_nasa_gibs_image(
        latitude=location["lat"],
        longitude=location["lon"],
        date="2023-06-01",
        zoom=10
    )

    if image:
        print(f"✅ Successfully fetched image: {image.size}")
        fetcher.save_image(image, "data/images/test_nasa.jpg")
    else:
        print("❌ Failed to fetch image")


if __name__ == "__main__":
    test_fetcher()
