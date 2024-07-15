import os
import requests
import csv
import xml.etree.ElementTree as ET

# List of known system field IDs
SYSTEM_FIELD_IDS = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40
]

# List of field types to exclude
EXCLUDE_FIELD_TYPES = [
    'subject', 'description', 'status', 'tickettype', 'priority', 'group', 'assignee', 'custom_status'
]

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

def is_custom_field(field_id):
    return field_id not in SYSTEM_FIELD_IDS

def download_custom_ticket_fields_to_csv(instances, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['subdomain', 'field_id', 'field_title', 'field_type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for instance in instances:
            subdomain = instance['subdomain']
            email = instance['email']
            token = instance['token']
            url = f'https://{subdomain}.zendesk.com/api/v2/ticket_fields.json'
            try:
                response = requests.get(url, auth=(email + '/token', token))
                response.raise_for_status()
                ticket_fields = response.json().get('ticket_fields', [])
                for field in ticket_fields:
                    field_id = field['id']
                    field_type = field['type']
                    if is_custom_field(field_id) and field_type not in EXCLUDE_FIELD_TYPES:
                        field_title = field['title']
                        writer.writerow({'subdomain': subdomain, 'field_id': field_id, 'field_title': field_title, 'field_type': field_type})
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch ticket fields for {subdomain}. Error: {e}")

def download_custom_dropdown_options_to_csv(instances, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['subdomain', 'field_name', 'field_id', 'option_id', 'option_value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for instance in instances:
            subdomain = instance['subdomain']
            email = instance['email']
            token = instance['token']
            url = f'https://{subdomain}.zendesk.com/api/v2/ticket_fields.json'
            try:
                response = requests.get(url, auth=(email + '/token', token))
                response.raise_for_status()
                ticket_fields = response.json().get('ticket_fields', [])
                for field in ticket_fields:
                    field_id = field['id']
                    field_type = field['type']
                    if is_custom_field(field_id) and field_type not in EXCLUDE_FIELD_TYPES:
                        field_name = field['title']
                        if field_type in ['tagger', 'dropdown']:
                            options_url = f'https://{subdomain}.zendesk.com/api/v2/ticket_fields/{field_id}/options.json'
                            try:
                                options_response = requests.get(options_url, auth=(email + '/token', token))
                                options_response.raise_for_status()
                                options = options_response.json().get('custom_field_options', [])
                                for option in options:
                                    option_id = option['id']
                                    option_value = option['name']
                                    writer.writerow({'subdomain': subdomain, 'field_name': field_name, 'field_id': field_id, 'option_id': option_id, 'option_value': option_value})
                            except requests.exceptions.RequestException as e:
                                print(f"Failed to fetch options for field ID {field_id} in subdomain {subdomain}. Error: {e}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch ticket fields for {subdomain}. Error: {e}")

if __name__ == "__main__":
    current_directory = os.getcwd()
    auth_filepath = os.path.join(current_directory, "d3v_prd_instances.xml")

    custom_ticket_fields_output_file = os.path.join(current_directory, "custom_ticket_fields.csv")
    custom_dropdown_options_output_file = os.path.join(current_directory, "custom_dropdown_options.csv")

    instances = load_instances_from_xml(auth_filepath)
    download_custom_ticket_fields_to_csv(instances, custom_ticket_fields_output_file)
    download_custom_dropdown_options_to_csv(instances, custom_dropdown_options_output_file)
