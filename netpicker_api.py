import requests

def get_auth_info():
    url = "https://sandbox.netpicker.io/api/v1/auth/info"
    
    try:
        response = requests.get(url)
        # response.raise_for_status()
        
        print("Response from auth/info:")
        print(response.json())
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_auth_info()
