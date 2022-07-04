"""This is the main module for Netorg generate."""

from merakiwrapper import MerakiWrapper
from registereddevicesloader import RegisteredDevicesLoader
from merakiactiveclientsloader import MerakiActiveClientsLoader
from merakifixedipreservationsloader import MerakiFixedIpReservationsLoader
from devicetableloader import DeviceTableLoader
from registereddevicesgenerator import RegisteredDevicesGenerator

class NetorgGenerator:
    """All things associated with Netorg generate"""

    def __init__(self, config):
        meraki_wrapper = MerakiWrapper(config['api_key'])
        registered_devices_loader = RegisteredDevicesLoader(config['devices_yml'])
        meraki_active_clients_loader = MerakiActiveClientsLoader(
            meraki_wrapper.dashboard,
            config['serial_id'],
            config['vlan_id'])
        meraki_fixed_ip_reservations_loader = MerakiFixedIpReservationsLoader(
            meraki_wrapper.dashboard,
            config['network_id'],
            config['vlan_id'])
        device_table_loader = DeviceTableLoader(
            registered_devices_loader,
            meraki_active_clients_loader,
            meraki_fixed_ip_reservations_loader)
        self.device_table = device_table_loader.load_all()
        self.devices_yml_path = config['devices_yml']

    def generate(self) :
        registered_devices_generator = RegisteredDevicesGenerator() 
        print(f'Generating devices.yml file at {self.devices_yml_path}')
        with open(self.devices_yml_path, 'w', encoding='utf8') as devices_yml_file:
            devices_yml_file.write(registered_devices_generator.generate(self.device_table))