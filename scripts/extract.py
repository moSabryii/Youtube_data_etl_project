import requests
import json
from datetime import date
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


def extract_video_data(video_ids):
    """
    Fetch detailed metadata for a list of video IDs from YouTube.

    This function requests multiple video details in batches (up to 50 per call),
    using the 'videos' endpoint. Each batch includes metadata such as title,
    publish date, duration, view count, likes, and comments.

    Args:
        video_ids (list): A list of YouTube video IDs.

    Returns:
        list[dict]: A list of dictionaries containing extracted video metadata.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the API request.
    """

    # Initialize a container for all extracted video data
    extracted_data = []

    # Helper function to yield successive chunks of video IDs (batch processing)
    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id : video_id + batch_size]

    try:
        # Process video IDs in manageable batches
        for batch in batch_list(video_ids, max_result):
            # Join list of IDs into a comma-separated string for the API request
            video_ids_str = ",".join(batch)

            # Construct API endpoint for retrieving detailed video data
            url = (
                f"https://youtube.googleapis.com/youtube/v3/videos?"
                f"part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"
            )

            # Execute the GET request and validate response
            response = requests.get(url)
            response.raise_for_status()

            # Decode the JSON response
            data = response.json()

            # Loop through each video in the response and extract structured fields
            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                # Map relevant attributes into a clean structured dictionary
                video_data = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "publishedAt": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "viewCount": statistics.get("viewCount", None),
                    "likeCount": statistics.get("likeCount", None),
                    "commentCount": statistics.get("commentCount", None),
                }

                # Append the current video's metadata to the results list
                extracted_data.append(video_data)

        # Return the final list containing all videos' metadata
        return extracted_data

    except requests.exceptions.RequestException as e:
        # Propagate any request-related exceptions upward
        raise e

def save_to_json(extracted_data):
    """
    Save the extracted video metadata to a JSON file.

    The file will be named with the current date and stored inside a 'data' folder.
    The folder is created automatically if it does not already exist.

    Args:
        extracted_data (list): List of dictionaries containing YouTube video data.
    """
    # Ensure the data folder exists to prevent file write errors
    os.makedirs("./data", exist_ok=True)  
    
    # Define the file path with today's date
    path = f"./data/YT_data_{date.today()}.json"
    
    # Inform the user that saving is in progress
    print(f"Saving {len(extracted_data)} videos to {path} ...")
    
    # Write data to the JSON file with proper formatting and UTF-8 encoding
    with open(path, "w", encoding="utf-8") as file:
        json.dump(extracted_data, file, indent=4, ensure_ascii=False)
    # Confirm successful file creation
    print("✅ File saved successfully!")

if __name__ == "__main__":
    # Run the extraction workflow only if this script is executed directly
    # (prevents automatic execution when imported as a module in other scripts)

    # Step 1: Get the channel's upload playlist ID
    playlistId = get_playlist_id()

    # Step 2: Retrieve all video IDs from that playlist
    video_ids = get_video_ids(playlistId)

    # Step 3: Extract and print detailed metadata for all retrieved videos
    video_data = extract_video_data(video_ids)
    
    save_to_json(video_data)
