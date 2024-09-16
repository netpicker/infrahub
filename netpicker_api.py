import requests
from infrahub_sdk.checks import InfrahubCheck


class Check(InfrahubCheck):
    query = "tags_check"

    def validate(self, data):
        login_url = 'http://127.0.0.1/api/v1/auth/jwt/login'
        info_url = "http://127.0.0.1/api/v1/auth/info"

        data = {
            'grant_type': 'password',
            'scope': 'openid access:api',
            'username': 'admin@admin.com',
            'password': '12345678'
        }

        try:
            # Login request
            login_response = requests.post(login_url, data=data, verify=False)
            login_response.raise_for_status()
            
            # Extract access token from login response
            access_token = login_response.json().get('access_token')
            
            if not access_token:
                self.log_error(message="Failed to obtain access token")
                return

            # Add access token to headers for info request
            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            # Info request
            info_response = requests.get(info_url, headers=headers, verify=False)
            info_response.raise_for_status()
            
            self.log_info(message="Response from auth/info:")
            self.log_info(message=info_response.json())
        
        except requests.RequestException as e:
            self.log_error(message=f"An error occurred: {e}")
