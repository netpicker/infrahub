import re
import requests
from infrahub_sdk.checks import InfrahubCheck


RE_TAG = re.compile(r"^color-[a-z]+")

class ColorTagsCheck(InfrahubCheck):
    query = "tags_check"

    def validate(self, data):
        url = "https://sandbox.netpicker.io/api/v1/auth/info"

        try:
            response = requests.get(url)
            # response.raise_for_status()
            
            print("Response from auth/info:")
            print(response.json())
        
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
