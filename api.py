import os
import platform


def api_host_informations():
    return [
        {"key": "Host Name", "value": str(os.name)},
        {"key": "System type", "value": str(platform.system())},
        {"key": "Release Version", "value": str(platform.release())},
    ]
