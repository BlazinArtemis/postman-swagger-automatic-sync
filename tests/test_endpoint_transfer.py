import unittest
import json
from postman_sync.endpoint_transfer import extract_endpoints, update_endpoints

class TestEndpointTransfer(unittest.TestCase):

    def setUp(self):
        # Sample data for testing
        self.old_data = {
            'collection': {
                'item': [
                    {
                        'name': 'Endpoint 1',
                        'request': {
                            'method': 'GET',
                            'url': {'raw': '/endpoint1'}
                        },
                        'event': [{'listen': 'test', 'script': {'exec': ['console.log("test1")']}}]
                    }
                ]
            }
        }
        self.new_data = {
            'collection': {
                'item': [
                    {
                        'name': 'Endpoint 1',
                        'request': {
                            'method': 'GET',
                            'url': {'raw': '/endpoint1'}
                        },
                        'event': []
                    },
                    {
                        'name': 'Endpoint 2',
                        'request': {
                            'method': 'POST',
                            'url': {'raw': '/endpoint2'}
                        },
                        'event': []
                    }
                ]
            }
        }

    def test_extract_endpoints(self):
        extracted = extract_endpoints(self.old_data['collection']['item'])
        self.assertIn('GET /endpoint1', extracted)
        self.assertEqual(extracted['GET /endpoint1']['request']['method'], 'GET')

    def test_extract_endpoints_empty(self):
        extracted = extract_endpoints([])
        self.assertEqual(extracted, {})

    def test_update_endpoints(self):
        old_endpoints = extract_endpoints(self.old_data['collection']['item'])
        stats = {
            'old_endpoints_count': len(old_endpoints),
            'updated_endpoints': [],
            'updated_events_count': 0,
        }
        updated_count = update_endpoints(self.new_data['collection']['item'], old_endpoints, stats)
        self.assertEqual(updated_count, 1)
        self.assertIn('GET /endpoint1', stats['updated_endpoints'])
        self.assertEqual(len(self.new_data['collection']['item'][0]['event']), 1)

    def test_update_endpoints_no_match(self):
        old_endpoints = extract_endpoints(self.old_data['collection']['item'])
        stats = {
            'old_endpoints_count': len(old_endpoints),
            'updated_endpoints': [],
            'updated_events_count': 0,
        }
        new_items = [
            {
                'name': 'Endpoint 3',
                'request': {
                    'method': 'PUT',
                    'url': {'raw': '/endpoint3'}
                },
                'event': []
            }
        ]
        updated_count = update_endpoints(new_items, old_endpoints, stats)
        self.assertEqual(updated_count, 0)
        self.assertNotIn('PUT /endpoint3', stats['updated_endpoints'])

if __name__ == '__main__':
    unittest.main()
