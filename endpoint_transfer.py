
import json

def extract_endpoints(items):
    endpoints = {}
    for item in items:
        if 'item' in item:
            endpoints.update(extract_endpoints(item['item']))
        elif 'request' in item:
            endpoint = f"{item['request']['method']} {item['request']['url']['raw']}"
            endpoints[endpoint] = item
    return endpoints

def update_endpoints(new_items, old_endpoints, stats):
    updated_count = 0
    for item in new_items:
        if 'item' in item:
            updated_count += update_endpoints(item['item'], old_endpoints, stats)
        elif 'request' in item:
            endpoint = f"{item['request']['method']} {item['request']['url']['raw']}"
            if endpoint in old_endpoints:
                item['event'] = old_endpoints[endpoint].get('event', [])
                updated_count += 1
                stats['updated_endpoints'].append(endpoint)
                stats['updated_events_count'] += len(item['event'])
                print(f"Updated events for endpoint: {endpoint}")
    return updated_count

def main(old_file_path, new_file_path, output_file_path):
    with open(old_file_path, 'r') as old_file:
        old_data = json.load(old_file)
    
    with open(new_file_path, 'r') as new_file:
        new_data = json.load(new_file)
    print(old_data)
    print("Extracting endpoints from the old file...")
    old_endpoints = extract_endpoints(old_data['collection']['item'])
    print(f"Extracted {len(old_endpoints)} endpoints from the old file.")
    stats = {
        'old_endpoints_count': len(old_endpoints),
        'updated_endpoints': [],
        'updated_events_count': 0,
    }

    print("Updating new file with events from old file...")
    updated_count = update_endpoints(new_data['collection']['item'], old_endpoints, stats)
    print(f"Updated {updated_count} endpoints in the new file.")

    with open(output_file_path, 'w') as output_file:
        json.dump(new_data, output_file, indent=4)
    
    print(f"Saved updated new file to {output_file_path}")
    
    print("Statistics:")
    print(f"Total endpoints in old file: {stats['old_endpoints_count']}")
    print(f"Total endpoints updated in new file: {updated_count}")
    print(f"Total events updated: {stats['updated_events_count']}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update Postman collection with events from another collection.")
    parser.add_argument("old_file", help="Path to the old Postman collection file.")
    parser.add_argument("new_file", help="Path to the new Postman collection file.")
    parser.add_argument("output_file", help="Path to save the updated Postman collection file.")

    args = parser.parse_args()
    
    main(args.old_file, args.new_file, args.output_file)