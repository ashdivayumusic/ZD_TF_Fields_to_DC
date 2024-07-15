import os
import csv
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

def create_dynamic_content_in_zendesk(instances, ticket_fields_file, dropdown_options_file):
    for instance in instances:
        subdomain = instance['subdomain']
        email = instance['email']
        token = instance['token']

        # Process ticket fields CSV
        with open(ticket_fields_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                field_name = row['field_title']
                dynamic_content_title = f'TF::Title-{field_name}'
                create_dynamic_content_item(subdomain, email, token, dynamic_content_title, field_name)

        # Process dropdown options CSV
        with open(dropdown_options_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                field_name = row['field_name']
                option_value = row['option_value']
                dynamic_content_title = f'TF::Title-{field_name}::{option_value}'
                create_dynamic_content_item(subdomain, email, token, dynamic_content_title, option_value)

def create_dynamic_content_item(subdomain, email, token, title, content):
    url = f'https://{subdomain}.zendesk.com/api/v2/dynamic_content/items'
    
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "item": {
            "name": title,
            "default_locale_id": 1,
            "variants": [
                {
                    "locale_id": 1,
                    "default": True,
                    "content": content
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, auth=(email + '/token', token), headers=headers, json=data)
        print(f"Request URL: {url}")
        print(f"Request Headers: {headers}")
        print(f"Request Data: {data}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        response.raise_for_status()
        print(f"Dynamic content created: {title}")
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 400:
            print(f"Bad Request: {response.json().get('error', 'Unknown error')}")
        elif response.status_code == 401:
            print("Unauthorized: Check your credentials")
        elif response.status_code == 403:
            print("Forbidden: You don't have permission to perform this action")
        elif response.status_code == 404:
            print("Not Found: The requested resource was not found")
        elif response.status_code == 500:
            print("Internal Server Error: The server encountered an error")
        else:
            print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

if __name__ == "__main__":
    current_directory = os.getcwd()
    auth_filepath = os.path.join(current_directory, "d3v_prd_instances.xml")

    ticket_fields_file = os.path.join(current_directory, "custom_ticket_fields.csv")
    dropdown_options_file = os.path.join(current_directory, "custom_dropdown_options.csv")

    instances = load_instances_from_xml(auth_filepath)
    create_dynamic_content_in_zendesk(instances, ticket_fields_file, dropdown_options_file)