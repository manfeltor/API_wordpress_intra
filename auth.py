import requests
from requests.auth import HTTPBasicAuth

username = 'ftorres'
password = 'RKFX LICa Boce NAnc bVhK QcOr'

api_url = 'https://intralog.com.ar/wp-json/wp/v2/users?context=edit'

response = requests.get(api_url, auth=HTTPBasicAuth(username, password))

if response.status_code == 200:
    print("Authentication successful!")
    print("Response Data:", response.json())
else:
    print(f"Failed to authenticate: {response.status_code}")
    print("Error message:", response.text)