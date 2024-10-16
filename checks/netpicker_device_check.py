import requests
from infrahub_sdk.checks import InfrahubCheck

# TODO: Eventually this will move to config / env
LOGIN_URL = "http://opsmill-netpicker.tailc018d.ts.net/api/v1/auth/jwt/login"
INFO_URL = "http://opsmill-netpicker.tailc018d.ts.net/api/v1/auth/info"
LOGIN_CREDENTIALS = {
    "grant_type": "password",
    "scope": "openid access:api",
    "username": "admin@admin.com",
    "password": "12345678",
}


class NetpickerDeviceInterfaceCheck(InfrahubCheck):
    query = "device_interface_details"

    def validate(self, data):
        # If there is any device to check
        if data["InfraDevice"]["count"] > 0:
            # Start the logic to verify Infrahub data
            try:
                # Authenticate to Netpicker API
                login_response = requests.post(
                    LOGIN_URL, data=LOGIN_CREDENTIALS, verify=False
                )
                login_response.raise_for_status()

                # Extract access token from login response
                access_token = login_response.json().get("access_token")

                if not access_token:
                    self.log_error(message="Failed to obtain access token")
                    return

                # Add access token to headers for info request
                headers = {"Authorization": f"Bearer {access_token}"}

                # Debug request
                debug_url = "http://opsmill-netpicker.tailc018d.ts.net/api/v1/policy/default/Infrahub_SDK/debug"
                debug_headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json',
                }
                python_code = """
@medium(
    name='rule_show_interfaces',
)
def rule_show_interfaces(configuration, commands, device):
    show_interfaces_output = device.cli('show interfaces')

    cli_interfaces = {}
    
    for line in show_interfaces_output.splitlines():
        if ' is ' in line:
            parts = line.split()
            interface_name = parts[0]
            if 'up' in line:
                interface_status = 'enabled'
            else:
                interface_status = 'disabled'
            cli_interfaces[interface_name] = interface_status
    
    assert False, cli_interfaces
"""

                debug_data = {
                    "name": "rule_show_interfaces",
                    "severity": "MEDIUM",
                    #"configuration": "example config here",
                    "ipaddress": "cisco_ios",
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

                # Compare interface status of device with data in Infrahub
                cli_interfaces = debug_response.json()['result']['excinfo']['message']

                # Log cli interface details
                self.log_info(f"CLI Interfaces: {', '.join(interfaces)}")
                
                # Search for device labeled 'cisco_ios' in Infrahub
                infrahub_device = None
                for edge in data["InfraDevice"]["edges"]:
                    device = edge["node"]
                    if device["display_label"] == "cisco_ios":
                        infrahub_device = device
                        break

                if infrahub_device is None:
                    self.log_error(message="No device with label 'cisco_ios' found.")
                    return

                # Now, you can continue with your processing using `infrahub_device`
                self.log_info(f"Found device: {infrahub_device['display_label']}")

                # You can now access interfaces or any other details from `infrahub_device`
                interfaces = [interface["node"]["name"]["value"] for interface in infrahub_device["interfaces"]["edges"]]

                # Log device interface details
                self.log_info(f"Interfaces: {', '.join(interfaces)}")
                
            
            except requests.RequestException as e:
                self.log_error(message=f"An error occurred: {e}")
            
            try:
                # Loop over devices
                for device in data["InfraDevice"]["edges"]:
                    device = device["node"]

                    interface_list: list[str] = []

                    # Loop over interfaces attached to that device
                    for interface in device["interfaces"]["edges"]:
                        interface = interface["node"]

                        # Here I can access name of my interface
                        interface_list.append(interface["name"]["value"])

                        # ... I can access various other things as mtu, speed, description ...


                    # Then can log verious things
                    self.log_info(
                        f"My device `{device['display_label']}` has `{str(device['interfaces']['count'])}` interfaces."
                    )
                    self.log_info(f"Interfaces: {', '.join(interface_list)}")

            except requests.RequestException as e:
                self.log_error(message=f"An error occurred: {e}")

        else:
            self.log_info("No device to check, all good!")
