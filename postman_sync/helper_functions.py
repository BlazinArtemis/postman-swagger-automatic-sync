import requests
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def cleanup_collection(collection_id, api_key):
    """
    Deletes a Postman collection using the provided collection ID and API key.

    Args:
        collection_id (str): The ID of the Postman collection to delete.
        api_key (str): The Postman API key.

    Returns:
        bool: True if the collection was successfully deleted, False otherwise.
    """
    url = f"https://api.getpostman.com/collections/{collection_id}"
    headers = {
        'X-Api-Key': api_key
    }
    
    try:
        logging.debug(f"Attempting to delete collection with ID: {collection_id}")
        response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            logging.info(f"Successfully deleted collection with ID: {collection_id}")
            return True
        else:
            logging.error(f"Failed to delete collection. Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Request to delete collection failed: {e}")
        return False

def get_collection_json(collection_id, api_key):
    """
    Fetches a Postman collection in JSON format using the provided collection ID and API key.

    Args:
        collection_id (str): The ID of the Postman collection to fetch.
        api_key (str): The Postman API key.

    Returns:
        dict: The JSON data of the Postman collection if successful, None otherwise.
    """
    url = f"https://api.getpostman.com/collections/{collection_id}"
    headers = {
        'X-Api-Key': api_key
    }

    try:
        logging.debug(f"Attempting to fetch collection with ID: {collection_id}")
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            logging.info(f"Successfully fetched collection with ID: {collection_id}")
            return response.json()
        else:
            logging.error(f"Failed to fetch collection. Status code: {response.status_code}, Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Request to fetch collection failed: {e}")
        return None


def fetch_swagger_json(swagger_url):
    """
    Fetches the Swagger JSON from the provided URL.

    Args:
        swagger_url (str): The URL of the Swagger JSON.

    Returns:
        dict: The Swagger JSON if successful, None otherwise.
    """
    try:
        logging.debug(f"Attempting to download Swagger JSON from: {swagger_url}")
        response = requests.get(swagger_url)

        if response.status_code == 200:
            swagger_json = response.json()
            logging.info("Successfully downloaded Swagger JSON.")
            return swagger_json
        else:
            logging.error(f"Failed to download Swagger JSON. Status code: {response.status_code}, Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to download Swagger JSON failed: {e}")
        return None

def create_collection_json(swagger_url, api_key):
    """
    Downloads a Swagger JSON from the provided URL, validates it, and creates a Postman collection using the Postman API.

    Args:
        swagger_url (str): The URL of the Swagger JSON.
        api_key (str): The Postman API key.

    Returns:
        str: The ID of the created Postman collection if successful, None otherwise.
    """
    swagger_json = fetch_swagger_json(swagger_url)
    if not swagger_json:
        return None

    if 'openapi' not in swagger_json and 'swagger' not in swagger_json:
        logging.error("Swagger JSON does not contain the necessary 'openapi' or 'swagger' version field.")
        return None

    logging.debug(f"Validated Swagger JSON: {json.dumps(swagger_json, indent=4)}")

    import_url = "https://api.getpostman.com/import/openapi"
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }

    payload = json.dumps({
        'type': 'json',
        'input': swagger_json
    })

    logging.debug(f"Payload for Postman API: {payload}")

    try:
        logging.debug("Attempting to create Postman collection with downloaded Swagger JSON.")
        response = requests.post(import_url, headers=headers, data=payload)

        if response.status_code == 200:
            response_json = response.json()
            logging.debug(f"Import Response JSON: {json.dumps(response_json, indent=4)}")
            if 'collections' in response_json and len(response_json['collections']) > 0:
                collection_id = response_json['collections'][0].get('uid')
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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Delete, fetch, or create a Postman collection using the Postman API.")
    parser.add_argument("action", choices=["delete", "fetch", "create"], help="Action to perform: 'delete', 'fetch', or 'create'.")
    parser.add_argument("api_key", help="The Postman API key.")
    parser.add_argument("--collection_id", help="The ID of the Postman collection (for 'delete' or 'fetch' actions).")
    parser.add_argument("--swagger_url", help="The URL of the Swagger JSON (for 'create' action).")

    args = parser.parse_args()
    
    if args.action == "delete":
        if cleanup_collection(args.collection_id, args.api_key):
            logging.info("Collection deleted successfully.")
        else:
            logging.error("Failed to delete the collection.")
    elif args.action == "fetch":
        collection_json = get_collection_json(args.collection_id, args.api_key)
        if collection_json:
            logging.info("Collection fetched successfully.")
            print(json.dumps(collection_json, indent=4))
        else:
            logging.error("Failed to fetch the collection.")
    elif args.action == "create":
        collection_id = create_collection_json(args.swagger_url, args.api_key)
        if collection_id:
            logging.info(f"Collection created successfully with ID: {collection_id}")
        else:
            logging.error("Failed to create the collection.")
