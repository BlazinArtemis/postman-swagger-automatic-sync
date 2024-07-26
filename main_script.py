import json
import os
import hashlib
import logging
import argparse
import requests
from datetime import datetime
from helper_functions import cleanup_collection, get_collection_json, create_collection_json
from endpoint_transfer import extract_endpoints, update_endpoints, main
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY_FILE = 'api_key.txt'
LINKS_FILE = 'links.json'
NEW_JSON_FILE = 'new.json'
OLD_JSON_FILE = 'old.json'
UPDATED_JSON_FILE = 'updated.json'

def save_api_key(api_key):
    """

    --- Now Depracated ---
    Saves the API key to a file.

    Args:
        api_key (str): The Postman API key.
    """
    with open(API_KEY_FILE, 'w') as file:
        file.write(api_key)
    logging.info("API key saved successfully.")

def load_api_key():
    """
    Loads the API key from an environment variable or a file.
    If not found, prompts the user to input the API key and saves it to a file.

    Returns:
        str: The Postman API key.
    """
    api_key = os.getenv('POSTMAN_API_KEY')
    if api_key:
        logging.info("API key loaded from environment variable.")
        return api_key

    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as file:
            api_key = file.read().strip()
            if api_key:
                logging.info("API key loaded from file.")
                return api_key

    logging.error("No API key found. Please set the POSTMAN_API_KEY environment variable or provide the API key.")
    api_key = input("Enter your Postman API key: ").strip()
    save_api_key(api_key)
    return api_key

    


def initialize_links_file():
    """
    Initializes the links file if it doesn't exist.
    """
    if not os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'w') as file:
            json.dump([], file)
        logging.info("Links file initialized.")

def load_links():
    """
    Loads the links from the file.

    Returns:
        list: A list of links.
    """
    with open(LINKS_FILE, 'r') as file:
        return json.load(file)

def save_links(links):
    """
    Saves the links to the file.

    Args:
        links (list): A list of links.
    """
    with open(LINKS_FILE, 'w') as file:
        json.dump(links, file, indent=4)
    logging.info("Links file updated.")

def hash_json(data):
    """
    Calculates the hash of a JSON object.

    Args:
        data (dict): The JSON object.

    Returns:
        str: The hash of the JSON object.
    """
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()

def create_collection_from_file(json_file_path, api_key):
    """
    Creates a Postman collection from a JSON file and returns the collection ID.

    Args:
        json_file_path (str): The path to the JSON file.
        api_key (str): The Postman API key.

    Returns:
        str: The ID of the created Postman collection if successful, None otherwise.
    """
    with open(json_file_path, 'rb') as file:
        json_data = json.load(file)

    import_url = "https://api.getpostman.com/collections"
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'collection': json_data['collection']
    }

    try:
        logging.debug(f"Attempting to create Postman collection with JSON file: {json_file_path}")
        response = requests.post(import_url, headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            logging.debug(f"Import Response JSON: {json.dumps(response_json, indent=4)}")
            if 'collection' in response_json and len(response_json['collection']) > 0:
                collection_id = response_json['collection'].get('uid')
                logging.info(f"Successfully created Postman collection with ID: {collection_id}")
                return collection_id
            else:
                logging.error("No collections found in the response.")
                return None
        else:
            logging.error(f"Failed to create Postman collection. Status code: {response.status_code}, Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to create Postman collection failed: {e}")
        return None

def main_code():
    """
    Main code execution function that processes all objects in the links file.
    """
    logging.info("Executing main_code function.")
    links = load_links()
    api_key = load_api_key()
    
    for entry in links:
        old_collection_uid = entry['Collection UID']
        link = entry['link']
        logging.debug(f"Processing link: {link} with old collection UID: {old_collection_uid}")

        try:
            response = requests.get(link)
            if response.status_code == 200:
                new_json = response.json()
                new_hash = hash_json(new_json)
                if new_hash == entry['hash']:
                    logging.info("No changes found. Moving on to the next object.")
                    continue
                else:
                    logging.info("Changes detected. Updating the collection.")
                    new_collection_id = create_collection_json(link, api_key)
                    if new_collection_id:
                        new_collection_json = get_collection_json(new_collection_id, api_key)
                        with open(NEW_JSON_FILE, 'w') as new_file:
                            json.dump(new_collection_json, new_file, indent=4)

                        cleanup_collection(new_collection_id, api_key)

                        old_collection_json = get_collection_json(old_collection_uid, api_key)
                        with open(OLD_JSON_FILE, 'w') as old_file:
                            json.dump(old_collection_json, old_file, indent=4)

                        main(OLD_JSON_FILE, NEW_JSON_FILE, UPDATED_JSON_FILE)

                        latest_collection_id = create_collection_from_file(UPDATED_JSON_FILE, api_key)

                        if latest_collection_id:
                            entry['Collection UID'] = latest_collection_id
                            entry['hash'] = new_hash
                            entry['Last Date Updated'] = datetime.now().isoformat()
                            save_links(links)
                            logging.info("Collection updated successfully.")
                        else:
                            logging.error("Failed to create the latest collection.")
            else:
                logging.error(f"Failed to download JSON from link. Status code: {response.status_code}, Response: {response.text}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Request to download JSON failed: {e}")

def new_entry(api_key, link):
    """
    Handles new entries without a collection UID.
    
    Args:
        api_key (str): The Postman API key.
        link (str): The Swagger JSON link.
    """
    logging.info(f"Executing new_entry function for link: {link}")

    try:
        # Download the JSON from the link
        logging.debug(f"Attempting to download JSON from: {link}")
        response = requests.get(link)
        if response.status_code == 200:
            json_data = response.json()
            json_hash = hash_json(json_data)
            logging.info("Successfully downloaded and hashed JSON.")
        else:
            logging.error(f"Failed to download JSON. Status code: {response.status_code}, Response: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to download JSON failed: {e}")
        return

    # Create a new collection with the downloaded JSON
    new_collection_id = create_collection_json(link, api_key)
    if not new_collection_id:
        logging.error("Failed to create a new collection from the link.")
        return

    # Create a new items object and add it to links.json
    new_entry = {
        "link": link,
        "hash": json_hash,
        "Collection UID": new_collection_id,
        "Last Date Updated": datetime.now().isoformat()
    }

    links = load_links()
    links.append(new_entry)
    save_links(links)
    logging.info(f"New entry added to links.json: {new_entry}")

def new_with_existing_collection(api_key, link, old_collection_uid):
    """
    Handles new entries with an existing collection UID.

    Args:
        api_key (str): The Postman API key.
        link (str): The Swagger JSON link.
        old_collection_uid (str): The existing Postman collection UID.
    """
    logging.info(f"Executing new_with_existing_collection function for link: {link} and collection UID: {old_collection_uid}")

    try:
        # Download the JSON from the link
        logging.debug(f"Attempting to download JSON from: {link}")
        response = requests.get(link)
        if response.status_code == 200:
            json_data = response.json()
            json_hash = hash_json(json_data)
            logging.info("Successfully downloaded and hashed JSON.")
        else:
            logging.error(f"Failed to download JSON. Status code: {response.status_code}, Response: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to download JSON failed: {e}")
        return

    # Create a new collection with the downloaded JSON
    new_collection_id = create_collection_json(link, api_key)
    if not new_collection_id:
        logging.error("Failed to create a new collection from the link.")
        return

    # Get the JSON of the newly created collection and store it in new.json
    new_collection_json = get_collection_json(new_collection_id, api_key)
    if not new_collection_json:
        logging.error("Failed to fetch the new collection JSON.")
        cleanup_collection(new_collection_id, api_key)
        return

    with open(NEW_JSON_FILE, 'w') as new_file:
        json.dump(new_collection_json, new_file, indent=4)
    logging.info(f"New collection JSON stored in {NEW_JSON_FILE}")

    # Clean up the newly created collection
    cleanup_collection(new_collection_id, api_key)

    # Get the JSON of the old collection and store it in old.json
    old_collection_json = get_collection_json(old_collection_uid, api_key)
    if not old_collection_json:
        logging.error("Failed to fetch the old collection JSON.")
        return

    with open(OLD_JSON_FILE, 'w') as old_file:
        json.dump(old_collection_json, old_file, indent=4)
    logging.info(f"Old collection JSON stored in {OLD_JSON_FILE}")

    # Run the main function from endpoint_transfer.py to update the collection
    main(OLD_JSON_FILE, NEW_JSON_FILE, UPDATED_JSON_FILE)
    logging.info(f"Updated JSON stored in {UPDATED_JSON_FILE}")

    # Create a new collection with the updated JSON
    latest_collection_id = create_collection_from_file(UPDATED_JSON_FILE, api_key)
    if not latest_collection_id:
        logging.error("Failed to create the latest collection.")
        return

    # Create a new items object and add it to links.json
    new_entry = {
        "link": link,
        "hash": json_hash,
        "Collection UID": latest_collection_id,
        "Last Date Updated": datetime.now().isoformat()
    }

    links = load_links()
    links.append(new_entry)
    save_links(links)
    logging.info(f"New entry added to links.json: {new_entry}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Postman collections with Swagger JSON links.")
    parser.add_argument("--link", help="The URL of the Swagger JSON.")
    # parser.add_argument("--api_key", help="The Postman API key.") Now Depracated
    parser.add_argument("--collection_id", help="The ID of the existing Postman collection.")

    args = parser.parse_args()

    initialize_links_file()
    api_key = load_api_key()

    if args.link:
        links = load_links()
        existing_entry = next((entry for entry in links if entry['link'] == args.link), None)
        
        if existing_entry:
            logging.warning("The link already exists in the system.")
        else:
            if args.collection_id:
                new_with_existing_collection(api_key, args.link, args.collection_id)
            else:
                new_entry(api_key, args.link)
    else:
        if api_key:
            main_code()
        else:
            logging.error("API key not provided and no API key stored in the system.")