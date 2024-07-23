import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import logging
import os
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from auth_vars import usrnm as a, passw as b, frmids as f

# Retrieve credentials and form IDs from environment variables
username = a
password = b
form_ids = f

# API base URL
api_url = 'https://intralog.com.ar/wp-json/custom/v1/form-submissions/'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define column renaming mapping
column_renaming = {
    'id': 'ID',
    'created_at': 'Creation Date',
    'updated_at': 'Update Date',
    'Razón Social': 'Company Name',
    'Nombre y Apellido': 'Full Name',
    'Teléfono': 'Phone',
    'Correo electrónico': 'Email',
    'Completa tu mensaje': 'Message',
    'Me interesa el servicio': 'Interested Service'
}

def get_form_submissions(api_url, username, password):
    try:
        # Make the API request
        response = requests.get(api_url, auth=HTTPBasicAuth(username, password))
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info(f"Successfully retrieved data from {api_url}")
            return response.json()
        else:
            logger.error(f"Failed to retrieve data from {api_url}: {response.status_code}")
            logger.error(f"Error message: {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Request failed for {api_url}: {e}")
        return None

def save_to_excel(data, output_file):
    try:
        # Rename columns according to the mapping
        data = data.rename(columns=column_renaming)

        if not os.path.exists(output_file):
            # Save new data to a new workbook
            data.to_excel(output_file, index=False, engine='openpyxl')
            logger.info(f"DataFrame saved as new file {output_file}")
        else:
            # Load the existing workbook
            book = load_workbook(output_file)
            sheet = book.active
            
            # Load existing data into a DataFrame
            data_rows = list(sheet.iter_rows(min_row=2, max_row=sheet.max_row, values_only=True))
            headers = [cell.value for cell in sheet[1]]
            existing_df = pd.DataFrame(data_rows, columns=headers)
            
            # Rename columns in existing DataFrame
            existing_df = existing_df.rename(columns=column_renaming)
            
            # Debug prints
            logger.info(f"Existing data headers: {existing_df.columns.tolist()}")
            logger.info(f"New data headers: {data.columns.tolist()}")
            
            # Merge new data with existing data, avoiding duplicates
            updated_df = pd.concat([existing_df, data]).drop_duplicates(keep='last')
            
            # Clear the existing data in the sheet
            sheet.delete_rows(2, sheet.max_row)
            
            # Convert the updated DataFrame to rows
            rows = dataframe_to_rows(updated_df, index=False, header=False)
            
            # Write the headers if they are not already present
            if not existing_df.empty:
                for c_idx, header in enumerate(updated_df.columns, 1):
                    sheet.cell(row=1, column=c_idx, value=header)
            
            # Write the updated rows to the sheet
            for r_idx, row in enumerate(rows, 2):
                for c_idx, value in enumerate(row, 1):
                    sheet.cell(row=r_idx, column=c_idx, value=value)
            
            # Save the workbook
            book.save(output_file)
            logger.info(f"DataFrame updated and saved as {output_file}")
    except Exception as e:
        logger.error(f"Failed to update the Excel file: {e}")

def main():
    all_data = pd.DataFrame()  # Initialize an empty DataFrame to hold all form submissions
    
    for form_id in form_ids:
        api_url = f'{api_url}{form_id}'
        data = get_form_submissions(api_url, username, password)
        if data:
            form_submissions = data.get('form_submissions', [])
            new_df = pd.DataFrame(form_submissions)
            new_df['form_id'] = form_id  # Add form_id to each record
            all_data = pd.concat([all_data, new_df])  # Combine all data into one DataFrame
    
    output_file = 'form_submissions.xlsx'
    save_to_excel(all_data, output_file)

if __name__ == "__main__":
    main()