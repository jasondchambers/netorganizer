import getpass
import os
import meraki
from ports import ConfigurationWizardPort

class ConfigurationWizardConsoleAdapter(ConfigurationWizardPort):

    def __init__(self):
        self.__config = {}

    # overriding abstract method
    def generate(self) -> dict:
        """Generate a configuration"""
        api_key = ConfigurationWizardConsoleAdapter.__get_api_key()
        meraki_wrapper = MerakiWrapper(api_key)
        meraki_wrapper.initialize(ConfigurationWizardConsoleAdapter.__choose_from_options)
        config = {}
        config['api_key'] = api_key
        config['devices_yml'] = ConfigurationWizardConsoleAdapter.__get_devices_yml_path()
        config['org_id'] = meraki_wrapper.get_org_id()
        config['network_id'] = meraki_wrapper.get_network_id()
        config['serial_id'] = meraki_wrapper.get_serial_id()
        config['vlan_id'] = meraki_wrapper.get_vlan_id()
        config['vlan_subnet'] = meraki_wrapper.get_vlan_subnet()
        return config

    @staticmethod
    def __get_api_key() -> str:
        # pylint: disable=line-too-long
        """Obtain the Meraki API key from the user"""
        print("You will need to obtain an API key. See the following for details:")
        print("https://developer.cisco.com/meraki/api-v1/#!authorization/obtaining-your-meraki-api-key")
        api_key = getpass.getpass('Meraki API key: ')
        return api_key

    @staticmethod
    def __choose_from_options(thing, choices) -> str:
        # pylint: disable=expression-not-assigned
        """Present options to user and return their selection."""
        print(f'Multiple {thing}s found:')
        [ print(f'{k} - {v}') for (k,v) in choices.items()]
        while True:
            selection = input(f'Which {thing}? : ')
            if selection in choices:
                break
        return selection
    
    @staticmethod
    def __get_devices_yml_path() -> str:
        """Obtain the fully qualified pathname for where to find/store known devices"""
        directory = ConfigurationWizardConsoleAdapter.__get_devices_yml_directory()
        filename = ConfigurationWizardConsoleAdapter.__get_devices_yml_filename()
        full_path = os.path.join(directory,filename)
        return full_path

    @staticmethod
    def __get_devices_yml_directory() -> str:
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
    def __get_devices_yml_filename() -> str:
        """Obtain the filename for where to find/store known devices"""
        default = 'devices.yml'
        device_yml_filename = input(f'Filename for where to find/store known devices [{default}]: ')
        if not device_yml_filename :
            device_yml_filename = default
        return device_yml_filename

class MerakiWrapperException(Exception) :
    # pylint: disable=missing-class-docstring
    pass

class InvalidApiKey(MerakiWrapperException) :
    # pylint: disable=missing-class-docstring
    pass

class FailedToInitializeMeraki(MerakiWrapperException) :
    # pylint: disable=missing-class-docstring
    pass

class NoOrganizationFound(MerakiWrapperException) :
    # pylint: disable=missing-class-docstring
    pass

class MoreThanOneOrganizationFound(MerakiWrapperException) :
    # pylint: disable=missing-class-docstring
    pass

class NoNetworksFound(MerakiWrapperException) :
    # pylint: disable=missing-class-docstring
    pass

class NoDevicesFound(MerakiWrapperException) :
    # pylint: disable=missing-class-docstring
    pass

class NoVlansFound(MerakiWrapperException) :
    # pylint: disable=missing-class-docstring
    pass

class MerakiWrapper :
    """Wrapper for the Meraki dashboard API."""

    def get_org_id(self) -> str:
        """Return the org id"""
        return self.org_id

    def get_network_id(self) -> str:
        """Return the network id"""
        return self.network_id

    def get_serial_id(self) -> str:
        """Return the device serial id"""
        return self.serial_id

    def get_vlan_id(self) -> str:
        """Return the vlan id"""
        return self.vlan_id

    def get_vlan_subnet(self) -> str:
        """Return the vlan subnet"""
        return self.vlan_subnet

    @staticmethod
    def find_org_id(dashboard) -> str:
        """Return the org ID."""
        organizations= dashboard.organizations.getOrganizations()
        if len(organizations) == 0 :
            raise NoOrganizationFound
        if len(organizations) > 1 :
            raise MoreThanOneOrganizationFound
        return organizations[0]["id"]

    @staticmethod
    def build_choices(menu) -> dict:
        """Build a choices dict where each menu item has a numeric key"""
        choice = 1
        choices = {}
        for network_name in menu:
            choices[str(choice)] = network_name
            choice += 1
        return choices

    @staticmethod
    def select_from_networks(networks, chooser_func) -> str:
        """Return the id of the network selected by the user"""
        network_names = [network['name'] for network in networks]
        choices = MerakiWrapper.build_choices(network_names)
        selection = chooser_func("network",choices)
        return networks[int(selection)-1]["id"]

    @staticmethod
    def select_from_devices(devices, chooser_func) -> str:
        """Return the serial id of the device selected by the user"""
        device_names = [ f'{device["model"]} - {device["serial"]}' for device in devices]
        choices = MerakiWrapper.build_choices(device_names)
        selection = chooser_func("device",choices)
        return devices[int(selection)-1]["serial"]

    @staticmethod
    def select_from_vlans(vlans, chooser_func) -> str:
        """Return the id of the VLAN selected by the user"""
        vlan_names = [ f'{vlan["name"]} - {vlan["subnet"]}' for vlan in vlans]
        choices = MerakiWrapper.build_choices(vlan_names)
        selection = chooser_func("VLAN",choices)
        return vlans[int(selection)-1]["id"]

    @staticmethod
    def find_network_id(dashboard, org_id, chooser_func) -> str:
        """Return the network id."""
        networks = dashboard.organizations.getOrganizationNetworks(org_id)
        if len(networks) == 0 :
            raise NoNetworksFound
        if len(networks) > 1 :
            return MerakiWrapper.select_from_networks(networks, chooser_func)
        return networks[0]["id"]

    @staticmethod
    def find_device_serial_id(dashboard, network_id, chooser_func) -> str:
        """Return the device serial id."""
        devices = dashboard.networks.getNetworkDevices(network_id)
        if len(devices) == 0 :
            raise NoDevicesFound
        if len(devices) > 1 :
            return MerakiWrapper.select_from_devices(devices, chooser_func)
        return devices[0]["serial"]

    @staticmethod
    def find_vlan_id(dashboard, network_id, chooser_func) -> str:
        """Return the VLAN id."""
        vlans = dashboard.appliance.getNetworkApplianceVlans(network_id)
        if len(vlans) == 0 :
            raise NoVlansFound
        if len(vlans) > 1 :
            return MerakiWrapper.select_from_vlans(vlans, chooser_func)
        return vlans[0]["id"]

    @staticmethod
    def find_vlan_subnet(dashboard, network_id, vlan_id) -> str:
        """Return the VLAN subnet."""
        vlan = dashboard.appliance.getNetworkApplianceVlan(network_id, str(vlan_id))
        return vlan['subnet']

    def __init__(self, api_key) :
        if not api_key :
            raise InvalidApiKey
        self.dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)
        self.org_id = ''
        self.network_id = ''
        self.serial_id = ''
        self.vlan_id = ''
        self.vlan_subnet = ''

    def initialize(self, chooser_func) :
        """Fully initialize the wrapper."""
        try :
            self.org_id = MerakiWrapper.find_org_id(self.dashboard)
            self.network_id = MerakiWrapper.find_network_id(
                self.dashboard, self.org_id, chooser_func)
            self.serial_id = MerakiWrapper.find_device_serial_id(
                self.dashboard, self.network_id, chooser_func)
            self.vlan_id = MerakiWrapper.find_vlan_id(
                self.dashboard, self.network_id, chooser_func)
            self.vlan_subnet = MerakiWrapper.find_vlan_subnet(
                self.dashboard,self.network_id,self.vlan_id)
        except meraki.exceptions.APIError as exc:
            print(f'Failed to initialize MerakiWrapper: {exc}')
            raise MerakiWrapperException from exc
