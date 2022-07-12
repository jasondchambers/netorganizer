"""This is the main module for Netorg scanning."""

from netorgmeraki import MerakiWrapper, MerakiActiveClientsLoader, MerakiFixedIpReservationsLoader
from registereddevicesloader import RegisteredDevicesLoader
from devicetable import DeviceTableLoader

class NetorgScanner:
    """All things associated with Netorg scanning"""

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

    def show_devices(self,df,state,guidance) :
        if df.shape[0] == 0:
            print(f'Did not find any devices that are {state}.')
        else:
            print(f'{df.shape[0]} device(s) are {state}. {guidance}:')
            for name in df['name']:
                print(f'     {name}')

    def report(self) :
        df = self.device_table.df
        need_registration_and_reservation_df = df.query('active and not reserved and not registered')
        self.show_devices(need_registration_and_reservation_df, 'active, not reserved and not registered', 'These will be registered as unclassified and assigned a reserved IP at the next sync')
        remove_reservation_df = df.query('reserved and not active and not registered')
        self.show_devices(remove_reservation_df, 'reserved, not active and not registered', 'The reserved IP will be removed at the next sync')
        need_registration_df = df.query('active and reserved and not registered')
        self.show_devices(need_registration_df, 'active, reserved and not registered', 'These will be registered as un-classified at the next sync')
        need_reservation_df = df.query('registered and not reserved and not active')
        self.show_devices(need_reservation_df, 'registered, not reserved and not active', 'A reserved IP will be created at the next sync')
        convert_to_static_df = df.query('registered and active and not reserved')
        self.show_devices(convert_to_static_df, 'registered, active and not reserved', 'The current IP will be converted to a static IP at the next sync')
        unclassified_df = df.query("active and group == 'unclassified'")
        self.show_devices(unclassified_df, 'active and unclassified', 'You should consider classifying them before the next sync')

