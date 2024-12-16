"""
This module processes media files in a specified directory.
It extracts The Movie Database (TMDB) IDs from filenames and lists available streaming providers.

It interacts with the TMDB API to fetch movie titles and streaming providers in the US.
It filters providers based on a predefined list.
The results are printed with clear indentation for readability.
"""

import os
import re
from typing import List
import requests
import utils

TMDB_URL_BASE = utils.get_config_value("TMDB_URL_BASE")
TMDB_API_KEY = utils.get_config_value("TMDB_API_KEY")
TIMEOUT = int(utils.get_config_value("TIMEOUT"))
PROVIDER_LIST = utils.get_config_value("PROVIDER_LIST")


def find_media_files(directory: str) -> List[str]:
    """
    Seaches the specified directory for media files.

    Args:
        directory (str): The directory to search in.

    Returns:
        List[str]: A list of filenames of media files found in the directory.
    """

    media_files = []
    for _, __, files in os.walk(directory):
        for file in files:
            media_files.append(file)
    return media_files


def get_tmdbid_from_filename(filename: str) -> str:
    """
    Extracts The Movie Database ID (TMDBID) from the filename using regex.

    Args:
        filename(str): The filename to extract TMDBID from.

    Returns:
        str: The TMDBID from the filename or None if not found.
    """
    regex = r"(?<=\[tmdbid-)\d+(?=\])"
    match = re.search(regex, filename)
    return match.group(0) if match else None


def get_movie_name_from_tmdbid(tmdbid: str) -> str:
    """
    Retrieves the movie title from TMDB by its TMDB ID.

    Args:
        tmdbid (str): The TMDB ID of the movie.

    Returns:
        str: The movie title.
    """
    url = f"{TMDB_URL_BASE}/movie/{tmdbid}?api_key={TMDB_API_KEY}"

    response = requests.get(url=url, timeout=TIMEOUT)

    movie_title = response.json().get("title", "Unknown Movie")

    return movie_title


def get_providers(tmdbid: str) -> List[str]:
    """
    Fetches a list of streaming providers for the given movie (by TMDB ID)

    Args:
        tmdbid (str): The TMDB ID of the movie.

    Returns:
        List[str]: A list of provider names for streaming the movie in the US.
    """
    url = f"{TMDB_URL_BASE}/movie/{tmdbid}/watch/providers?api_key={TMDB_API_KEY}"

    try:
        response = requests.get(url=url, timeout=TIMEOUT)
        response.raise_for_status()  # Raise exception for HTTP errors
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []

    # Check if the 'results' and 'US' keys exist in the response
    results_us = response.json().get("results", {}).get("US", {})
    streaming_providers = results_us.get("flatrate", [])
    return [
        provider["provider_name"]
        for provider in streaming_providers
        if provider["provider_name"] in PROVIDER_LIST
    ]


def main(directory: str):
    """
    Main function to process all media files in a directory, extract their TMDB IDs,
    retrieve the movie name and streaming providers, and print the results with indentation.
    """
    media_files = find_media_files(directory=directory)
    for media_file in media_files:
        movie = os.path.basename(media_file)
        tmdbid = get_tmdbid_from_filename(movie)

        if tmdbid:
            movie_name = get_movie_name_from_tmdbid(tmdbid)
            streaming_providers = get_providers(tmdbid)
            print(f"Movie: {movie_name}")
            if streaming_providers:
                print("\tStreaming Providers:")
                for provider in streaming_providers:
                    print(f"\t\t- {provider}")
            else:
                print("\tNo streaming providers found")
        else:
            print(f"TMDB ID not found in filename: {movie}")
        print()


if __name__ == "__main__":
    # Test usage
    DIRECTORY = "/mnt/media/media/movies"

    main(directory=DIRECTORY)
