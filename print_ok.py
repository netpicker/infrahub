import requests
from infrahub_sdk.checks import InfrahubCheck


class PrintOKCheck(InfrahubCheck):
    query = "tags_check"

    def validate(self, data):
        print('OK!')
