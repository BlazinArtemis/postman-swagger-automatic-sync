import unittest
from unittest.mock import patch, Mock
from postman_sync.helper_functions import cleanup_collection, get_collection_json, fetch_swagger_json, create_collection_json

class TestHelperFunctions(unittest.TestCase):

    @patch('postman_sync.helper_functions.requests.delete')
    def test_cleanup_collection(self, mock_delete):
        mock_delete.return_value = Mock(status_code=200)
        result = cleanup_collection('collection_id', 'api_key')
        self.assertTrue(result)

    @patch('postman_sync.helper_functions.requests.delete')
    def test_cleanup_collection_fail(self, mock_delete):
        mock_delete.return_value = Mock(status_code=404)
        result = cleanup_collection('collection_id', 'api_key')
        self.assertFalse(result)

    @patch('postman_sync.helper_functions.requests.get')
    def test_get_collection_json(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=Mock(return_value={'collection': {}}))
        result = get_collection_json('collection_id', 'api_key')
        self.assertIsNotNone(result)
        self.assertIn('collection', result)

    @patch('postman_sync.helper_functions.requests.get')
    def test_get_collection_json_fail(self, mock_get):
        mock_get.return_value = Mock(status_code=404)
        result = get_collection_json('collection_id', 'api_key')
        self.assertIsNone(result)

    @patch('postman_sync.helper_functions.requests.get')
    def test_fetch_swagger_json(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=Mock(return_value={'swagger': '2.0'}))
        result = fetch_swagger_json('http://example.com/swagger.json')
        self.assertIsNotNone(result)
        self.assertIn('swagger', result)

    @patch('postman_sync.helper_functions.requests.get')
    def test_fetch_swagger_json_fail(self, mock_get):
        mock_get.return_value = Mock(status_code=404)
        result = fetch_swagger_json('http://example.com/swagger.json')
        self.assertIsNone(result)

    @patch('postman_sync.helper_functions.requests.post')
    @patch('postman_sync.helper_functions.fetch_swagger_json')
    def test_create_collection_json(self, mock_fetch, mock_post):
        mock_fetch.return_value = {'swagger': '2.0'}
        mock_post.return_value = Mock(status_code=200, json=Mock(return_value={'collections': [{'uid': 'new_collection_id'}]}))
        result = create_collection_json('http://example.com/swagger.json', 'api_key')
        self.assertEqual(result, 'new_collection_id')

    @patch('postman_sync.helper_functions.requests.post')
    @patch('postman_sync.helper_functions.fetch_swagger_json')
    def test_create_collection_json_fail(self, mock_fetch, mock_post):
        mock_fetch.return_value = {'swagger': '2.0'}
        mock_post.return_value = Mock(status_code=400)
        result = create_collection_json('http://example.com/swagger.json', 'api_key')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
