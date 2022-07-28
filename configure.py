"""This is the main module for Netorg configuration."""

import os
import getpass
import json

import requests
from netorgmeraki import MerakiWrapper
from netorgsna import FailedToLogin, SnaSession

class NetorgConfigurator :
    """All things associated with configuring Netorg"""

    def __init__(self) -> None:
        self.__config = {}
        self.__get_api_key_func = NetorgConfigurator.default_get_api_key_func
        self.__choose_from_options_func = NetorgConfigurator.default_choose_from_options_func

    def set_get_api_key_func(self, get_api_key_func) -> None:
        """Over-ride default_get_api_func() with a custom function"""
        self.__get_api_key_func = get_api_key_func

    def set_choose_from_options_func(self, choose_from_options_func) -> None:
        """Over-ride default_choose_from_options_func() with a custom function"""
        self.__choose_from_options_func = choose_from_options_func

    def get_config(self) -> dict:
        """Return the current config (may have either been generated or loaded)."""
        return self.__config

    @staticmethod
    def default_get_api_key_func() -> str:
        # pylint: disable=line-too-long
        """Obtain the Meraki API key from the user"""
        print("You will need to obtain an API key. See the following for details:")
        print("https://developer.cisco.com/meraki/api-v1/#!authorization/obtaining-your-meraki-api-key")
        api_key = getpass.getpass('Meraki API key: ')
        return api_key

    @staticmethod
    def default_choose_from_options_func(thing, choices) -> str:
        # pylint: disable=expression-not-assigned
        """Present options to user and return their selection."""
        print(f'Multiple {thing}s found:')
        [ print(f'{k} - {v}') for (k,v) in choices.items() ]
        while True:
            selection = input(f'Which {thing}? : ')
            if selection in choices:
                break
        return selection

    def generate(self) -> None:
        """Generate a configuration"""
        api_key = self.__get_api_key_func()
        meraki_wrapper = MerakiWrapper(api_key)
        meraki_wrapper.initialize(self.__choose_from_options_func)
        self.__config = {}
        self.__config['api_key'] = api_key
        self.__config['devices_yml'] = NetorgConfigurator.get_devices_yml_path()
        self.__config['org_id'] = meraki_wrapper.get_org_id()
        self.__config['network_id'] = meraki_wrapper.get_network_id()
        self.__config['serial_id'] = meraki_wrapper.get_serial_id()
        self.__config['vlan_id'] = meraki_wrapper.get_vlan_id()
        self.__config['vlan_subnet'] = meraki_wrapper.get_vlan_subnet()
        self.generate_sna_config()

    def generate_sna_config(self):
        """Generate Secure Network Analytics config."""
        while True:
            answer = input('Do you want to configure Secure Network Analytics? (y/n) [n]:')
            if not answer or answer == 'n' or answer == 'N':
                break
            if answer in ('y', 'Y'):
                self.__config['sna.manager.host'] = input('Manager host: ')
                self.__config['sna.manager.username'] = input('Manager username: ')
                self.__config['sna.manager.password'] = getpass.getpass('Manager password: ')
                if self.isvalid_sna_config():
                    break
                self.remove_sna_config()

    def isvalid_sna_config(self) -> bool:
        """Return true if the SNA config is valid."""
        # pylint: disable=line-too-long
        try:
            sna_session = SnaSession(self.__config['sna.manager.host'])
            sna_session.login(self.__config['sna.manager.username'],
                              self.__config['sna.manager.password'])
            sna_session.logout()
            print('Secure Network Analytics configuration is valid')
            return True
        except FailedToLogin:
            print(f'Failed to login to Secure Network Analytics Manager at {self.__config["sna.manager.host"]}')
            return False
        except requests.exceptions.ConnectionError:
            print(f'Invalid or unreachable Secure Network Analytics Manager host {self.__config["sna.manager.host"]}')
            return False

    def remove_sna_config(self) -> None:
        """Remove the SNA configuration items from the config."""
        self.__config.pop('sna.manager.host')
        self.__config.pop('sna.manager.username')
        self.__config.pop('sna.manager.password')

    def get_config_filename(self) -> str:
        """Return the fully qualified config filename e.g. /a/b/.netorg.cfg"""
        directory = os.path.expanduser('~')
        filename = '.netorg.cfg'
        return os.path.join(directory, filename)

    def load(self) -> None:
        """Load configuration."""
        config_filename = self.get_config_filename()
        print(f'Loading config file {config_filename}')
        with open(config_filename, 'r', encoding='utf8') as netorg_config_file:
            self.__config = json.load(netorg_config_file)

    def save(self) -> None:
        """Save configuration."""
        ref = self.get_config()
        if ref:
            config_filename = self.get_config_filename()
            print(f'Saving config file {config_filename}')
            with open(config_filename, 'w', encoding='utf8') as netorg_config_file:
                netorg_config_file.write(json.dumps(ref, indent=2))

    @staticmethod
    def get_devices_yml_path() -> str:
        """Obtain the fully qualified pathname for where to find/store known devices"""
        directory = NetorgConfigurator.get_devices_yml_directory()
        filename = NetorgConfigurator.get_devices_yml_filename()
        full_path = os.path.join(directory,filename)
        return full_path

    @staticmethod
    def get_devices_yml_directory() -> str:
        """Obtain the directory for where to find/store known devices"""
        default = os.path.expanduser('~')
        while True:
            prompt = f'Directory for where to find/store known devices [{default}]: '
            device_yml_directory = input(prompt)
            if not device_yml_directory:
                return default
            if os.path.isdir(device_yml_directory):
                return device_yml_directory

    @staticmethod
    def get_devices_yml_filename() -> str:
        """Obtain the filename for where to find/store known devices"""
        default = 'devices.yml'
        device_yml_filename = input(f'Filename for where to find/store known devices [{default}]: ')
        if not device_yml_filename:
            device_yml_filename = default
        return device_yml_filename
