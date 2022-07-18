"""Module for creating DeviceTableLoaders."""

from devicetable import DeviceTableLoader
from knowndevicesloader import KnownDevicesLoader
from netorgmeraki import MerakiActiveClientsLoader, MerakiFixedIpReservationsLoader, MerakiWrapper

def create(config) -> DeviceTableLoader:
    """Create a DeviceTableLoader."""
    meraki_wrapper = MerakiWrapper(config['api_key'])
    known_devices_loader = KnownDevicesLoader(config['devices_yml'])
    meraki_active_clients_loader = MerakiActiveClientsLoader(
        meraki_wrapper.dashboard,
        config['serial_id'],
        config['vlan_id'])
    meraki_fixed_ip_reservations_loader = MerakiFixedIpReservationsLoader(
        meraki_wrapper.dashboard,
        config['network_id'],
        config['vlan_id'])
    return DeviceTableLoader(
        known_devices_loader,
        meraki_active_clients_loader,
        meraki_fixed_ip_reservations_loader)
