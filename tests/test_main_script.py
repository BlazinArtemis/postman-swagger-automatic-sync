import unittest
from unittest.mock import patch, mock_open, Mock
import json



from postman_sync.main_script import main_code, new_entry, new_with_existing_collection, save_links

class TestMainScript(unittest.TestCase):

    @patch('postman_sync.main_script.load_api_key', return_value='test_api_key')
    @patch('postman_sync.main_script.requests.get')
    @patch('postman_sync.main_script.requests.post')
    @patch('postman_sync.main_script.create_collection_json')
    @patch('postman_sync.main_script.get_collection_json')
    @patch('postman_sync.main_script.cleanup_collection')
    @patch('postman_sync.main_script.save_links')
    @patch('postman_sync.main_script.load_links')
    @patch('os.path.exists', return_value=True)
    def test_main_code(self, mock_exists, mock_load_links, mock_save_links, mock_cleanup, mock_get_collection_json, mock_create_collection_json, mock_requests_post, mock_requests_get, mock_load_api_key):
        links = [{
            'Collection UID': 'old_uid',
            'link': 'http://example.com',
            'hash': 'old_hash',
            'Last Date Updated': '2023-08-01T00:00:00'
        }]
        new_json = {'collection': {'item': []}}
        new_collection_id = 'new_uid'

        # Mocking requests
        mock_requests_get.return_value = Mock(status_code=200, headers={'Content-Type': 'application/json'})
        mock_requests_get.return_value.json.return_value = new_json
        mock_requests_post.return_value = Mock(status_code=200, headers={'Content-Type': 'application/json'})
        mock_requests_post.return_value.json.return_value = {'collections': [{'uid': new_collection_id}]}
        mock_create_collection_json.return_value = new_collection_id
        mock_get_collection_json.side_effect = [new_json, new_json]
        mock_load_links.return_value = links

        # Mock the open function for reading files
        mock_file_open = mock_open(read_data=json.dumps(new_json))
        with patch('builtins.open', mock_file_open) as mock_file:
            main_code()

        # Check that the file was opened and written to
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called()

    @patch('postman_sync.main_script.load_api_key', return_value='test_api_key')
    @patch('postman_sync.main_script.requests.get')
    @patch('postman_sync.main_script.requests.post')
    @patch('postman_sync.main_script.save_links')
    @patch('postman_sync.main_script.load_links')
    @patch('os.path.exists', return_value=True)
    def test_new_entry(self, mock_exists, mock_load_links, mock_save_links, mock_requests_post, mock_requests_get, mock_load_api_key):
        links = []
        new_json = {'swagger': '2.0', 'paths': {}}
        new_collection_id = 'new_uid'

        # Mocking requests
        mock_requests_get.return_value = Mock(status_code=200, headers={'Content-Type': 'application/json'})
        mock_requests_get.return_value.json.return_value = new_json
        mock_requests_post.return_value = Mock(status_code=200, headers={'Content-Type': 'application/json'})
        mock_requests_post.return_value.json.return_value = {'collections': [{'uid': new_collection_id}]}
        mock_load_links.return_value = links

        # Mock the open function for reading files
        mock_file_open = mock_open(read_data=json.dumps(new_json))
        with patch('builtins.open', mock_file_open) as mock_file:
            new_entry('test_api_key', 'http://example.com')

        # Check that the file was opened and written to
        # mock_file.assert_called()
        # handle = mock_file()
        # handle.write.assert_called()

    @patch('postman_sync.main_script.load_api_key', return_value='test_api_key')
    @patch('postman_sync.main_script.requests.get')
    @patch('postman_sync.main_script.requests.post')
    @patch('postman_sync.main_script.get_collection_json')
    @patch('postman_sync.main_script.cleanup_collection')
    @patch('postman_sync.main_script.save_links')
    @patch('postman_sync.main_script.load_links')
    @patch('os.path.exists', return_value=True)
    def test_new_with_existing_collection(self, mock_exists, mock_load_links, mock_save_links, mock_cleanup, mock_get_collection_json, mock_requests_post, mock_requests_get, mock_load_api_key):
        links = []
        new_json = {'swagger': '2.0', 'paths': {}, 'collection': {'item': []}}
        new_collection_id = 'new_uid'
        old_collection_id = 'old_uid'

        # Mocking requests
        mock_requests_get.return_value = Mock(status_code=200, headers={'Content-Type': 'application/json'})
        mock_requests_get.return_value.json.return_value = new_json
        mock_requests_post.return_value = Mock(status_code=200, headers={'Content-Type': 'application/json'})
        mock_requests_post.return_value.json.return_value = {'collections': [{'uid': new_collection_id}]}
        mock_get_collection_json.side_effect = [new_json, new_json, new_json, new_json]
        mock_load_links.return_value = links

        # Mock the open function for reading files
        mock_file_open = mock_open(read_data=json.dumps(new_json))
        with patch('builtins.open', mock_file_open) as mock_file:
            new_with_existing_collection('test_api_key', 'http://example.com', old_collection_id)

        # Check that the file was opened and written to
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called()

    @patch('builtins.open', new_callable=mock_open)
    def test_save_links(self, mock_open):
        links = [{'link': 'http://example.com'}]

        # Call the function
        save_links(links)

        # Ensure the open function was called with the correct arguments
        mock_open.assert_called_once_with('links.json', 'w')

        # Collect all write calls into a single call argument
        handle = mock_open()
        write_calls = handle.write.call_args_list

        # Concatenate all the write call arguments into a single string
        written_content = ''.join(call[0][0] for call in write_calls)

        # Check that the write method was called with the correct data
        self.assertEqual(json.dumps(links, indent=4), written_content)


if __name__ == '__main__':
    unittest.main()
