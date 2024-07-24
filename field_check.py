import requests
from requests.auth import HTTPBasicAuth
import logging
from auth_vars import usrnm as a, passw as b, frmids as f
from pprint import pprint

# Retrieve credentials and form IDs from environment variables
username = a
password = b
form_ids = f

# API base URL
base_api_url = 'https://intralog.com.ar/wp-json/custom/v1/form-submissions/'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_form_fields(api_url, username, password):
    try:
        # Make the API request
        response = requests.get(api_url, auth=HTTPBasicAuth(username, password))
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info(f"Successfully retrieved data from {api_url}")
            data = response.json()
            form_submissions = data.get('form_submissions', [])
            if form_submissions:
                # Get the first submission to extract field names
                first_submission = form_submissions[0]
                field_names = list(first_submission.keys())
                return field_names
            else:
                logger.warning(f"No submissions found for {api_url}")
                return []
        else:
            logger.error(f"Failed to retrieve data from {api_url}: {response.status_code}")
            logger.error(f"Error message: {response.text}")
            return []
    except requests.RequestException as e:
        logger.error(f"Request failed for {api_url}: {e}")
        return []

def main():
    for form_id in form_ids:
        full_api_url = f'{base_api_url}{form_id}'
        field_names = get_form_fields(full_api_url, username, password)
        if field_names:
            print(f"Field names for form {form_id}:")
            pprint(field_names)
        else:
            print(f"No field names retrieved for form {form_id}")

if __name__ == "__main__":
    main()