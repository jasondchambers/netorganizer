"""Module for loading known devices."""

import os.path
import yaml

class KnownDevicesLoader:
    """Load the file containing known devices."""

    def __init__(self,filename='./devices.yml') -> None:
        self.filename = filename

    def load(self) -> list:
        """Load the file containing known devices."""
        device_list = []
        if os.path.exists(self.filename) :
            print(f'Loading known devices from {self.filename}')
            with open(self.filename, encoding='utf8') as known_devices_file:
                data = yaml.load(known_devices_file, Loader=yaml.FullLoader)
                devices = data['devices']
                device_group_names = devices.keys()
                for device_group_name in device_group_names:
                    devices_in_group = devices[device_group_name]
                    for device_in_group in devices_in_group:
                        device_in_group_str = device_in_group.split(',')
                        device_name = device_in_group_str[0]
                        device_mac = device_in_group_str[1]
                        device = {
                            'name': device_name,
                            'mac': device_mac,
                            'group': device_group_name}
                        device_list.append(device)
        else:
            print(f'{self.filename} not found')
        return device_list

    def load_from_string(self,string) -> list:
        """Load known devices from a string containing the YAML (used for testing)."""
        device_list = []
        data = yaml.safe_load(string)
        devices = data['devices']
        device_group_names = devices.keys()
        for device_group_name in device_group_names:
            devices_in_group = devices[device_group_name]
            for device_in_group in devices_in_group:
                device_in_group_str = device_in_group.split(',')
                device_name = device_in_group_str[0]
                device_mac = device_in_group_str[1]
                device = {
                    'name': device_name,
                    'mac': device_mac,
                    'group': device_group_name}
                device_list.append(device)
        return device_list
