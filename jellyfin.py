import json
import re
from typing import Dict
import requests

JELLYFIN_URL = "http://jellyfin.xander:8096"
JELLYFIN_API = "5fa99d4fa673446aa2681d89ce45a0e3"
TIMEOUT = 10


class TMDBIDNotFoundError(Exception):
    """Custom exception for when a TMDB ID is not found in the movie path."""

    pass


def build_jellyfin_url(endpoint: str) -> str:
    """
    Constructs a full Jellyfin API URL using the base URL, API key, and endpoint.

    Args:
        endpoint (str): The API endpoint to append.

    Returns:
        str: The complete Jellyfin API URL.
    """
    return f"{JELLYFIN_URL}/{endpoint}?api_key={JELLYFIN_API}"


def get_jellyfin_info() -> Dict[str, str]:
    """
    Fetches and returns system information from the Jellyfin API.

    This function builds the Jellyfin API URL for the 'System/Info' endpoint,
    sends a GET request with a timeout, and returns the system information if successful.
    If the request fails, it raises a JellyfinAPIError.

    Args:
        timeout (float): Maximum time in seconds to wait for the response. Defaults to 10.0.

    Returns:
        dict[str, str]: System information if the request is successful.

    Raises:
        JellyfinAPIError: If the request fails or the server returns a non-200 status code.
    """
    url = build_jellyfin_url("System/Info/Public")

    try:
        response = requests.get(url=url, timeout=TIMEOUT)
        info = response.json()
        return info
    except requests.RequestException as e:
        print(f"Jellyfin API Error: {e}")
    except TimeoutError as e:
        print(f"Jellyfin API Timed Out: {e}")


def test_jellyfin() -> None:
    """
    Tests the Jellyfin API connection by retrieving system information.

    This function fetches system information from the Jellyfin API,
    extracts the server name and local address, and prints a confirmation message.

    Raises:
        KeyError: If expected keys are missing in the response data.
        JellyfinAPIError: If the API request fails.
    """
    info = get_jellyfin_info()

    try:
        server_name = info["ServerName"]
        server_addr = info["LocalAddress"]
        print(
            f"Found Jellyfin server named '{server_name}' on local address '{server_addr}'."
        )
    except KeyError as e:
        print(f"Error: Missing expected key in response data: {e}")


def get_jellyfin_movies() -> Dict[str, str]:
    url = build_jellyfin_url("Items")
    params = {
        "Type": "Movie",
        "ExcludeItemTypes": "Folder, Episode, Season, Series",
        "Fields": "Path",
        "MediaTypes": "Video",
        "IsFolder": "false",
        "Recursive": "true",
        "Limit": 1000,
    }

    try:
        response = requests.get(url=url, params=params, timeout=TIMEOUT).json()
        movies = response["Items"]
        movies_tmdb_ids = {}
        for item in movies:
            path = item["Path"]
            tmdb_id = re.search(r"(?<=\[tmdbid-)\d+(?=\])", path)

            if tmdb_id:
                movies_tmdb_ids[item["Name"]] = tmdb_id.group(0)
            else:
                movies_tmdb_ids[item["Name"]] = path
                # raise TMDBIDNotFoundError(
                #     f"TMDB ID not found for movie '{item['Name']}' in path '{path}'"
                # )
        return movies_tmdb_ids
        # return json.dumps(response, indent=4)
    except requests.RequestException as e:
        print(f"Jellyfin API Error: {e}")
    except TimeoutError as e:
        print(f"Jellyfin API Timed Out: {e}")
    except TMDBIDNotFoundError as e:
        print(f"Error: {e}")


try:
    movies_dict = get_jellyfin_movies()
    for key, value in movies_dict.items():
        print(f"{key}: {value}")
except TypeError as e:
    print(f"failed: {e}")
