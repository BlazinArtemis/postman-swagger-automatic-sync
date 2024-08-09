
# Postman x Swagger Automatic Sync Manager

Ever wanted to automatically update your Postman Collections once there is a change on your swagger file ( while retaining your tests ). 
This script can be run as a cron job that checks your swagger.json links for any changes in your api and If a change is noticed, It creates a new Postman Collection with all your tests intact. 

## How the tool works

This tool manages a list of Swagger JSON links, continuously checking for changes and updating Postman collections accordingly.

## Key Features:
- Link Management: Add Swagger JSON links to a list by running the script with the --link option. These links are stored in a file for continuous monitoring.
- Change Detection: The tool periodically checks each stored link for changes in the Swagger JSON file.
- Postman Collection Updates: Upon detecting changes, the tool updates the corresponding Postman collection:
    - A new Postman collection is created with the updated Swagger endpoints.
    - Tests from the old collection are transferred to the new collection.
    - The updated collection, containing both new endpoints and existing tests, is saved.


## How to Run It

### Prerequisites

- Python 3.x
```sh
- pip install -r requirements.txt
```

### Running the Script

0. **Set the API Key as an Environment Variable**

   You can set the Postman API key as an environment variable named `POSTMAN_API_KEY`.

   #### On Windows
   ```sh
   set POSTMAN_API_KEY=your_postman_api_key
   ```

   #### On macOS/Linux
   ```sh
   export POSTMAN_API_KEY=your_postman_api_key
   ```

### Three Ways of running it

1. **Add a New Entry with a New Collection**:
   ```sh
   python main_script.py --link <swagger_json_link> 

   or 

   python main_script.py --l <swagger_json_link> 
   ```

2. **Add a New Entry with an Existing Collection**:
   ```sh
   python main_script.py --link <swagger_json_link>  --collection_id <existing_collection_id>

   or 

   python main_script.py --l <swagger_json_link>  --c <existing_collection_id>
   ```

3. **Run the Main Code** (requires the API key to be already set):
   ```sh
   python main_script.py
   ```

4 **Alternatively, Store the API Key in a File (Not Safe )**

   If you don't want to use an environment variable, you can store the API key in a file named `api_key.txt` in the same directory as the script. The script will prompt you to enter and save the API key if it doesn't find it in the environment variables or the file.

   - **Create the `api_key.txt` File Manually**:
     - Create a file named `api_key.txt`.
     - Open the file and paste your Postman API key inside it.
     - Save and close the file.

**Note, If you have already inputted your API Key once, you can run without including --api-key**

## How to Add to Cron Job

To continually check for changes to your Swagger JSON links, you can set up a cron job to run the script at regular intervals.

1. Open your crontab file:
   ```sh
   crontab -e
   ```

2. Add a new cron job to run the script periodically. For example, to run the script every hour, add:
   ```sh
   0 * * * * /usr/bin/python3 /path/to/your/main_script.py
   ```

   Replace `/path/to/your/main_script.py` with the actual path to your script.

3. Save and exit the crontab file.

## Things to Work On

- Edit the name of the collection worked on (old and latest) so QA can know the latest and how to delete it.
- Write tests to ensure the script works as expected.
- Write a function and argument to delete a link from the list.
- Maybe rather than create a new collection with the updated tests, edit the current collection. ( Fear is Back-Up, Will think about this later. )
- ~~ Allow Postman Key to work with enviroment variables as the file storing is not ideal.~~ - DONE 

## Shoutouts
- [@dftaiwo](https://github.com/dftaiwo)
- [@detunjiSamuel](https://github.com/detunjiSamuel)


## Due to Postman, Version of OpenAPI or Swagger has to be there as well as the version number of your API
The Swagger JSON should include the `openapi` or `swagger` field and the version number of your API. For example:
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "FastAPI",
    "version": "0.1.0"
  },
  ...
}
```

## How It Works and Explanation of Functions

### Components

1. **API Key Management**: The API key is saved to and loaded from a file (`api_key.txt`).
2. **Links File**: The script uses `links.json` to store information about Swagger JSON links and corresponding Postman collections.
3. **Hashing**: The script calculates a hash of the Swagger JSON content to detect changes.
4. **Functions**:
   - `save_api_key(api_key)`: Saves the API key to a file.
   - `load_api_key()`: Loads the API key from an environment variable or a file. Prompts the user to input the key if not found.
   - `initialize_links_file()`: Initializes the links file if it doesn't exist.
   - `load_links()`: Loads the links from the file.
   - `save_links(links)`: Saves the links to the file.
   - `hash_json(data)`: Calculates the hash of a JSON object.
   - `create_collection_from_file(json_file_path, api_key)`: Creates a Postman collection from a JSON file.
   - `main_code()`: Main function to process and update collections.
   - `new_entry(api_key, link)`: Handles new entries without a collection UID.
   - `new_with_existing_collection(api_key, link, old_collection_uid)`: Handles new entries with an existing collection UID.

### Workflow

1. **Adding a New Entry**:
   - Download the Swagger JSON from the link.
   - Calculate its hash.
   - Create a new Postman collection from the JSON.
   - Store the link, hash, collection UID, and last updated date in `links.json`.

2. **Updating an Existing Entry**:
   - Download the Swagger JSON from the link.
   - Calculate its hash.
   - Compare the hash with the stored hash.
   - If different, create a new collection, get the JSON, and update the existing collection.

3. **Main Execution**:
   - Processes all entries in `links.json` to check for updates and apply changes as necessary.

## Logging

The script uses Python's logging module to provide detailed logs of its operations. Logs include information about API requests, JSON processing, and updates to collections. This helps in debugging and ensuring that the script runs correctly.

## Conclusion

This script automates the management of Postman collections using Swagger JSON links ensuring all your tests are intact. By setting up a cron job, you can ensure that your collections are always up-to-date with the latest changes in your Swagger definitions.
