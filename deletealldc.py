import os
import requests
import xml.etree.ElementTree as ET

def load_instances_from_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    instances = []
    for instance in root.findall('instance'):
        subdomain = instance.find('subdomain').text
        email = instance.find('email').text
        token = instance.find('token').text
        instances.append({'subdomain': subdomain, 'email': email, 'token': token})
    return instances

def get_dynamic_content_items(subdomain, email, token):
    url = f'https://{subdomain}.zendesk.com/api/v2/dynamic_content/items.json'
    
    try:
        response = requests.get(url, auth=(email + '/token', token))
        response.raise_for_status()
        return response.json().get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch dynamic content items for {subdomain}. Error: {e}")
        return []

def delete_dynamic_content_item(subdomain, email, token, item_id):
    url = f'https://{subdomain}.zendesk.com/api/v2/dynamic_content/items/{item_id}'
    
    try:
        response = requests.delete(url, auth=(email + '/token', token))
        response.raise_for_status()
        print(f"Deleted dynamic content item ID: {item_id}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to delete dynamic content item ID {item_id} for {subdomain}. Error: {e}")

if __name__ == "__main__":
    current_directory = os.getcwd()
    auth_filepath = os.path.join(current_directory, "d3v_prd_instances.xml")

    instances = load_instances_from_xml(auth_filepath)
    
    for instance in instances:
        subdomain = instance['subdomain']
        email = instance['email']
        token = instance['token']
        
        items = get_dynamic_content_items(subdomain, email, token)
        for item in items:
            delete_dynamic_content_item(subdomain, email, token, item['id'])
