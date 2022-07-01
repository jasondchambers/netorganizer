"""This is the main module for Netorg reporting."""

from merakiwrapper import MerakiWrapper
from registereddevicesloader import RegisteredDevicesLoader
from merakiactiveclientsloader import MerakiActiveClientsLoader
from merakifixedipreservationsloader import MerakiFixedIpReservationsLoader
from devicetableloader import DeviceTableLoader

class NetorgReporter:
    """All things associated with Netorg reporting"""

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