#!/usr/bin/env python3
import time
import requests
import argparse
import os
import random
from datetime import datetime, timedelta

def get_missing_movies(radarr_url, api_key):
    """Fetch the list of missing movies from Radarr."""
    endpoint = f"{radarr_url}/api/v3/wanted/missing"
    params = {
        'apikey': api_key,
        'page': 1,
        'pageSize': 1000
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('records', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching missing movies: {e}")
        return []

def search_movie(radarr_url, api_key, movie_id):
    """Trigger a search for a specific movie in Radarr."""
    endpoint = f"{radarr_url}/api/v3/command"
    payload = {
        'name': 'MoviesSearch',
        'movieIds': [movie_id]
    }
    try:
        response = requests.post(endpoint, json=payload, params={'apikey': api_key})
        response.raise_for_status()
        print(f"Search triggered for movie ID {movie_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error triggering search for movie ID {movie_id}: {e}")

def load_searched_movies(file_path):
    """Load the list of searched movie IDs from a file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def save_searched_movie(file_path, movie_id):
    """Save a searched movie ID to the file."""
    with open(file_path, 'a') as file:
        file.write(f"{movie_id}\n")

def is_movie_released(movie):
    """Check if the movie has been released based on its status in Radarr."""
    status = movie.get('status')
    return status and status.lower() == 'released'

def parse_time_left(time_left_str):
    """Parse SABnzbd time left string (h:mm:ss) into seconds."""
    try:
        h, m, s = map(int, time_left_str.split(':'))
        return timedelta(hours=h, minutes=m, seconds=s).total_seconds()
    except ValueError:
        print(f"Error parsing time left: {time_left_str}")
        return float('inf')

def get_sabnzbd_queue_info(sabnzbd_url, api_key):
    """Fetch the SABnzbd queue information."""
    endpoint = f"{sabnzbd_url}/api"
    params = {
        'apikey': api_key,
        'mode': 'queue',
        'output': 'json'
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        queue_slots = data.get('queue', {}).get('slots', [])

        for slot in queue_slots:
            if not slot.get('status', '').lower() == 'paused':
                time_left_str = slot.get('timeleft', '0:00:00')
                return len(queue_slots), parse_time_left(time_left_str)
        
        return len(queue_slots), 0  # All items are paused, no ETA
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SABnzbd queue information: {e}")
        return float('inf'), float('inf')  # Return large numbers on error to prevent triggering a search

def main():
    parser = argparse.ArgumentParser(description="Radarr Missing Movies Search Script")
    parser.add_argument("--radurl", required=True, help="The base URL of the Radarr instance")
    parser.add_argument("--radapikey", required=True, help="The API key for Radarr")
    parser.add_argument("--saburl", required=True, help="The base URL of the SABnzbd instance")
    parser.add_argument("--sabapikey", required=True, help="The API key for SABnzbd")
    parser.add_argument("--queue-limit", type=int, default=5, help="The maximum number of items allowed in the SABnzbd queue before triggering a search (default: 5)")
    parser.add_argument("--sab-sleep", type=int, default=60, help="Minimum sleep interval in seconds between SABnzbd queue checks (default: 60)")
    parser.add_argument("--radarr-sleep", type=int, default=60, help="Sleep interval in seconds between Radarr searches (default: 60)")
    parser.add_argument("--no-movies-sleep", type=int, default=3600, help="Sleep interval in seconds when no missing movies are found (default: 3600)")
    args = parser.parse_args()

    radarr_url = args.radurl
    radarr_api_key = args.radapikey
    sabnzbd_url = args.saburl
    sabnzbd_api_key = args.sabapikey
    queue_limit = args.queue_limit
    sab_sleep = args.sab_sleep
    radarr_sleep = args.radarr_sleep
    no_movies_sleep = args.no_movies_sleep

    archive_file = "./archive.lst"

    # Load previously searched movie IDs
    searched_movies = load_searched_movies(archive_file)

    while True:
        # Fetch the list of missing movies
        missing_movies = get_missing_movies(radarr_url, radarr_api_key)

        if not missing_movies:
            print(f"No missing movies found. Sleeping for {no_movies_sleep} seconds before checking again.")
            time.sleep(no_movies_sleep)
            continue

        # Shuffle the list for random ordering
        random.shuffle(missing_movies)

        for movie in missing_movies:
            movie_id = movie['id']
            movie_title = movie['title']

            if str(movie_id) in searched_movies:
                print(f"Skipping already searched movie: {movie_title} (ID: {movie_id})")
                continue

            if not is_movie_released(movie):
                print(f"Skipping unreleased movie: {movie_title} (ID: {movie_id})")
                save_searched_movie(archive_file, movie_id)
                searched_movies.add(str(movie_id))
                continue

            # Check SABnzbd queue size and time
            while True:
                queue_size, current_item_time_left = get_sabnzbd_queue_info(sabnzbd_url, sabnzbd_api_key)
                if queue_size < queue_limit:
                    break

                sleep_time = max(sab_sleep, current_item_time_left)
                print(f"SABnzbd queue has {queue_size} items, first item time left: {current_item_time_left}s. Waiting {sleep_time} seconds before checking again.")
                time.sleep(sleep_time)  # Wait before checking again

            print(f"Triggering search for missing movie: {movie_title} (ID: {movie_id})")
            search_movie(radarr_url, radarr_api_key, movie_id)

            # Save the movie ID to the archive
            save_searched_movie(archive_file, movie_id)
            searched_movies.add(str(movie_id))

            # Rate limit Radarr searches
            time.sleep(radarr_sleep)

if __name__ == "__main__":
    main()

