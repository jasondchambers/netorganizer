"""This is the main module for Netorg configuration."""

import os
import getpass
import json
from merakiwrapper import MerakiWrapper

class NetorgConfigurator:
    """All things associated with configuring Netorg"""

    def __init__(self):
        self.config = {}

    def get_config(self) -> dict:
        """Return the current config (may have either been generated or loaded)."""
        return self.config

    @staticmethod
    def get_api_key() -> str:
        """Obtain the Meraki API key from the user"""
        print ("You will need to obtain an API key. See the following for details:")
        print ("https://developer.cisco.com/meraki/api-v1/#!authorization/obtaining-your-meraki-api-key")
        api_key = getpass.getpass('Meraki API key: ')
        return api_key

    @staticmethod
    def choose_from_options(thing, choices) -> str:
        """Present options to user and return their selection."""
        print(f'Multiple {thing}s found:')
        [ print(f'{k} - {v}') for (k,v) in choices.items()]
        while True: 
            selection = input(f'Which {thing}? : ') 
            if selection in choices:
                break
        return selection

    def generate(self, get_api_key_func=get_api_key, choose_from_options_func=choose_from_options) -> None:
        """Generate a configuration"""
        api_key = get_api_key_func()
        meraki_wrapper = MerakiWrapper(api_key)
        meraki_wrapper.initialize(choose_from_options_func)
        self.config = {}
        self.config['api_key'] = api_key
        self.config['devices_yml'] = NetorgConfigurator.get_devices_yml_path()
        self.config['org_id'] = meraki_wrapper.get_org_id()
        self.config['network_id'] = meraki_wrapper.get_network_id()
        self.config['serial_id'] = meraki_wrapper.get_serial_id()
        self.config['vlan_id'] = meraki_wrapper.get_vlan_id()
        self.config['vlan_subnet'] = meraki_wrapper.get_vlan_subnet()

    def get_config_filename(self) -> str:
        directory = os.path.expanduser('~')
        filename = '.netorg.cfg'
        return os.path.join(directory,filename)

    def load(self) -> None:
        """Load configuration."""
        print(f'Loading config file {self.get_config_filename()}')
        with open(self.get_config_filename(), encoding='utf8') as json_file:
            self.config = json.load(json_file)

    def save(self):
        """Save configuration."""
        if self.get_config():
            print(f'Saving config file {self.get_config_filename()}')
            with open(self.get_config_filename(), 'w', encoding='utf8') as netorg_config_file: 
                netorg_config_file.write(json.dumps(self.get_config(), indent=2))

    @staticmethod
    def get_devices_yml_path() -> str:
        """Obtain the fully qualified pathname for where to find/store registered devices"""
        directory = NetorgConfigurator.get_devices_yml_directory()
        filename = NetorgConfigurator.get_devices_yml_filename()
        full_path = os.path.join(directory,filename)
        return full_path

    @staticmethod
    def get_devices_yml_directory() -> str:
        """Obtain the directory for where to find/store registered devices"""
        default = os.path.expanduser('~')
        while True:
            device_yml_directory = input(f'Directory for where to find/store registered devices [{default}]: ')
            if not device_yml_directory:
                return default
            if os.path.isdir(device_yml_directory):
                return device_yml_directory

    @staticmethod
    def get_devices_yml_filename() -> str:
        """Obtain the filename for where to find/store registered devices"""
        default = 'devices.yml'
        device_yml_filename = input(f'Filename for where to find/store registered devices [{default}]: ')
        if not device_yml_filename :
            device_yml_filename = default
        return device_yml_filename
