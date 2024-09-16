import requests
from infrahub_sdk.checks import InfrahubCheck


class Check(InfrahubCheck):
    query = "tags_check"

    def validate(self, data):
        login_url = 'http://opsmill-netpicker.tailc018d.ts.net/api/v1/auth/jwt/login'
        info_url = "http://opsmill-netpicker.tailc018d.ts.net/api/v1/auth/info"

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

            # Debug request
            debug_url = "http://opsmill-netpicker.tailc018d.ts.net/api/v1/policy/default/Infrahub_SDK/debug"
            debug_headers = {
                'Accept': 'application/json, text/plain, */*',
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            python_code = """@medium(
    name='rule_show_interfaces',
)
def rule_show_interfaces(configuration, commands, device):
    assert configuration == False, 'Error message'
"""

            debug_data = {
                "name": "rule_show_interfaces",
                "severity": "MEDIUM",
                "configuration": "example config here",
                #"ipaddress": "cisco_ios",
                "command": None,
                "ruleset": "default",
                "definition": {
                    "code": python_code
                }
            }

            debug_response = requests.post(debug_url, headers=debug_headers, json=debug_data, verify=False)
            debug_response.raise_for_status()

            self.log_info(message="Response from debug endpoint:")
            self.log_info(message=debug_response.json())
        
        except requests.RequestException as e:
            self.log_error(message=f"An error occurred: {e}")
