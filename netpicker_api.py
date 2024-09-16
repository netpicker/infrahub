import requests
from infrahub_sdk.checks import InfrahubCheck


class Check(InfrahubCheck):
    query = "tags_check"

    def validate(self, data):
        url = "https://sandbox.netpicker.io/api/v1/auth/info"

        try:
            response = requests.get(url)
            # response.raise_for_status()
            
            self.log_info(message="Response from auth/info:")
            self.log_info(message=response.json())
        
        except requests.RequestException as e:
            self.log_error(message=f"An error occurred: {e}")
