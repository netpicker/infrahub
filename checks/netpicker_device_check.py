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
    query = "device_details"

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

                    # TODO: Implement Netpicker API call, I guess somewhere here with device & interface data

                    # Then can log verious things
                    self.log_info(
                        f"My device `{device['display_label']}` has `{str(device['interfaces']['count'])}` interfaces."
                    )
                    self.log_info(f"Interfaces: {', '.join(interface_list)}")

            except requests.RequestException as e:
                self.log_error(message=f"An error occurred: {e}")

        else:
            self.log_info("No device to check, all good!")
