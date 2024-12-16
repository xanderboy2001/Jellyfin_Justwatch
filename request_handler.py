from flask import Flask, request, jsonify
from utils import get_config_value
import requests
import jellyfin_checker

REJECT_MSG = "Movie is available on the following streaming services:"
ACCPET_MSG = "Movie is not available on any streaming services"

JELLYSEERR_URL_BASE = get_config_value("JELLYSEERR_URL_BASE")
JELLYSEERR_API_KEY = get_config_value("JELLYSEERR_API_KEY")

TIMEOUT = get_config_value("TIMEOUT")

BIND_ADDRESS = get_config_value("BIND_ADDRESS")
PORT = int(get_config_value("PORT"))

app = Flask(__name__)


def check_movie_on_services(tmdbid: str) -> tuple[bool, list[str]]:
    """Check if the movie is available on streaming services.

    Args:
        tmdbid (str): The TMDB ID of the movie.

    Returns:
        tuple[bool, list[str]]: A tuple containing a boolean indicating availability
        and a list of available providers.
    """
    providers = jellyfin_checker.get_providers(tmdbid)
    if providers:
        print(f"Available streaming services: {providers}")
        return True, providers
    else:
        print("No streaming services found.")
        return False, []


def update_request_status(request_id: str, status: str) -> None:
    """Update the request status on Jellyseerr.

    Args:
        request_id (str): The request ID from Jellyseerr.
        status (str): The new status to set (e.g., "approve" or "decline").
    """
    url = f"{JELLYSEERR_URL_BASE}/request/{request_id}/{status}"
    headers = {"X-Api-Key": JELLYSEERR_API_KEY}
    response = requests.post(url, headers=headers, timeout=TIMEOUT)

    if response.status_code == 200:
        print(f"Request {request_id} {status} successfully!")
    else:
        print(
            f"Error updating request {request_id} status. {response.status_code} - {response.text}"
        )


@app.route("/webhook", methods=["POST"])
def webhook_listener():
    """Handle webhook requests from Jellyseerr.

    Returns:
        Response: A JSON response indicating the outcome of the webhook event.
    """
    # Receive request data from Jellyseerr
    data = request.json

    if data.get("notification_type") == "TEST_NOTIFICATION":
        return (
            jsonify({"status": "received", "message": "Test notification received."}),
            200,
        )

    media = data.get("media", {})
    tmdbid = media.get("tmdbId", {})

    if not tmdbid:
        return jsonify({"error": "No TMDB ID provided"}), 400

    # Check if movie is on streaming services
    is_available, providers = check_movie_on_services(tmdbid)

    request_id = data["request"]["request_id"]

    if is_available:
        provider_list_joined = ", ".join(providers)

        update_request_status(request_id, "decline")

        return (
            jsonify(
                {
                    "status": "rejected",
                    "message": f"{REJECT_MSG} {provider_list_joined}.",
                }
            ),
            200,
        )
    else:
        update_request_status(request_id, "approve")
        return jsonify({"status": "accepted", "message": ACCPET_MSG})


if __name__ == "__main__":
    app.run(host=BIND_ADDRESS, port=PORT)
