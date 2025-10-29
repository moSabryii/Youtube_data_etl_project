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

# Maximum number of results to fetch per API request (YouTube API limit is 50)
max_result = 50


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
        # print(json.dumps(data, indent=4))

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


def get_video_ids(playlistId):
    """
    Retrieve all video IDs from a given YouTube playlist.

    This function handles pagination to collect every video in the playlist,
    up to the API's limits (each request returns up to 50 items).

    Args:
        playlistId (str): The ID of the YouTube playlist to fetch videos from.

    Returns:
        list: A list containing all video IDs from the playlist.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the API request.
    """

    # Base URL for the playlistItems endpoint
    base_url = (
        f"https://youtube.googleapis.com/youtube/v3/playlistItems?"
        f"part=contentDetails&maxResults={max_result}&playlistId={playlistId}&key={API_KEY}"
    )

    # Initialize an empty list to collect video IDs
    video_ids = []

    # Pagination token, used to fetch the next page of results if available
    pageToken = None

    try:
        while True:
            # Construct URL dynamically with the current page token if it exists
            url = base_url
            if pageToken:
                url += f"&pageToken={pageToken}"

            # Make the API request
            response = requests.get(url)
            response.raise_for_status()

            # Parse the JSON response into a Python dictionary
            data = response.json()

            # Extract video IDs from the current batch of playlist items
            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            # Check if there’s another page of results
            pageToken = data.get('nextPageToken')

            # Exit loop when no further pages exist
            if not pageToken:
                break

        # Return the complete list of collected video IDs
        return video_ids

    except requests.exceptions.RequestException as e:
        # Re-raise the exception to be handled by the caller or global error handler
        raise e


if __name__ == "__main__":
    # Run the extraction workflow only if this script is executed directly
    # (prevents automatic execution when imported as a module in other scripts)
    playlistId = get_playlist_id()

    # Fetch and store all video IDs for the retrieved playlist
    video_ids = get_video_ids(playlistId)
