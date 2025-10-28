import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
# This allows storing sensitive information like API keys securely
load_dotenv(dotenv_path="./.env")

# Retrieve the YouTube API key from environment variables
API_KEY = os.getenv("API_KEY")

# The YouTube channel handle for which we want to fetch the upload playlist ID
CHANNEL_HANDLE = "MrBeast"


def get_playlist_id():
    """
    Fetch the 'uploads' playlist ID for a given YouTube channel handle.

    The 'uploads' playlist contains all videos uploaded by the channel.
    This function uses the YouTube Data API v3 'channels' endpoint.

    Returns:
        str: The playlist ID of the channel's uploads.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the API request.
    """

    try:
        # Construct the URL for the YouTube Data API call
        url = (
            f"https://youtube.googleapis.com/youtube/v3/channels?"
            f"part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
        )

        # Make the GET request to the YouTube API
        response = requests.get(url)

        # Raise an exception for HTTP errors (status codes 4xx or 5xx)
        response.raise_for_status()

        # Parse the response JSON into a Python dictionary
        data = response.json()

        # Optional: Print the JSON data in a formatted way for debugging
        print(json.dumps(data, indent=4))

        # Navigate through the JSON structure to get the 'uploads' playlist ID
        channel_items = data["items"][0]
        channel_playlist_id = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]

        # Print the playlist ID for reference
        print(channel_playlist_id)

        # Return the playlist ID so it can be used elsewhere in the program
        return channel_playlist_id

    except requests.exceptions.RequestException as e:
        # If any request-related exception occurs, re-raise it for higher-level handling
        raise e


if __name__ == "__main__":
    # Run the function only if this script is executed directly
    # This prevents execution if the script is imported as a module
    get_playlist_id()
