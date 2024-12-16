"""
utils.py

This module contains shared constants and configuration settings used across the project.

Variables:
    TMDB_URL_BASE (str): Base URL for The Movie Database (TMDB) API requests.
    TMDB_API_KEY (str): API key for authenticating requests to the TMDB API.
    TIMEOUT (int): Request timeout in seconds for API calls.
    PROVIDER_LIST (List[str]): A list of supported streaming providers.

Usage:
    Import this module to access common configuration values and avoid hardcoding 
    them in multiple places throughout the project.
"""

TMDB_URL_BASE = "https://api.themoviedb.org/3"
TMDB_API_KEY = "7357404c261cefb23312ded89a07353e"
TIMEOUT = 10
PROIDER_LIST = [
    "Netflix basic with Ads",
    "Hulu",
    "Disney Plus",
    "Amazon Prime Video",
    "Max",
    "Apple TV",
    "Apple TV Plus",
]
