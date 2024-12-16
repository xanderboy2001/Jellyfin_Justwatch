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

from configparser import ConfigParser, NoOptionError, NoSectionError
import os
from typing import List

DEFAULT_CONFIG_PATH = "./deniarr.config"


def get_config() -> ConfigParser:
    """
    Reads the existing config file or creates a default one if it doesn't exist.

    Returns:
        ConfigParser: The loaded config object.
    """

    config = ConfigParser()

    if not os.path.exists(DEFAULT_CONFIG_PATH):
        write_default_config()

    # Read config file and return config object
    config.read(DEFAULT_CONFIG_PATH)
    return config


def write_default_config():
    """
    Writes a default config file if one doesn't exist.
    """
    config = ConfigParser()
    config["GENERAL"] = {
        "TMDB_URL_BASE": "https://api.themoviedb.org/3",
        "TMDB_API_KEY": "7357404c261cefb23312ded89a07353e",
        "TIMEOUT": "10",
        "PROVIDER_LIST": [
            "Netflix basic with Ads",
            "Hulu",
            "Disney Plus",
            "Amazon Prime Video",
            "Max",
            "Apple TV",
            "Apple TV Plus",
        ],
        "CONFIG_PATH": "deniarr.config",
    }
    with open(DEFAULT_CONFIG_PATH, "w", encoding="UTF-8") as config_file:
        config.write(config_file)


def get_config_value(option: str, section: str = "GENERAL") -> str:
    """
    Retrieves a specific config value.

    Args:
        section (str): The section name in the config file.
        option (str): The option to retrieve from the section.

    Returns:
        str: The config value.
    """
    config = get_config()
    if not config.has_section(section):
        raise NoSectionError(section)
    if not config.has_option(section, option):
        raise NoOptionError(option, section)
    return config.get(section, option)


def get_config_options(section: str = "GENERAL") -> List[str]:
    """
    Retrieves all configuration options from a specified section.

    Args:
        section (str): The section name in the configuration file.

    Returns:
        List[str]: A list of option names from the specified section.

    Raises:
        configparser.NoSectionError: If the section is not found in the configuration file.
    """
    config = get_config()
    if not config.has_section(section):
        raise NoSectionError(section)
    return config.options(section)


if __name__ == "__main__":
    print(get_config_options())
    print(get_config_value("CONFIG_PATH"))
