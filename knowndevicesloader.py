"""Module for loading known devices."""

from typing import Generator
import os.path
import yaml

class KnownDevicesLoader:
    """Load known devices."""

    def __init__(self, filename='./devices.yml') -> None:
        self.filename = filename

    def __load_data(self, data) -> Generator[dict, None, None]:
        """Load known devices."""
        if not isinstance(data, dict):
            raise ValueError("Invalid YAML")
        if 'devices' not in data:
            raise ValueError("Invalid YAML")
        devices = data['devices']
        for device_group_name, devices_in_group in devices.items():
            for device_in_group in devices_in_group:
                device_in_group_str = device_in_group.split(',')
                device_name = device_in_group_str[0]
                device_mac = device_in_group_str[1]
                device = {
                    'name': device_name,
                    'mac': device_mac,
                    'group': device_group_name}
                yield device

    def load(self) -> Generator[dict, None, None]:
        """Load known devices from (YAML) file."""
        if not os.path.exists(self.filename):
            print(f'{self.filename} not found')
            return
        print(f'Loading known devices from {self.filename}')
        data = []
        with open(self.filename, encoding='utf8') as known_devices_file:
            data = yaml.load(known_devices_file, Loader=yaml.FullLoader) # TODO buffered read using ruamel in future
        yield from self.__load_data(data)

    def load_from_string(self,string) -> Generator[dict, None, None]:
        """Load known devices from (YAML) string."""
        data = yaml.safe_load(string) # TODO buffered read using ruamel in future
        yield from self.__load_data(data)
