"""This is the main module for Netorg scanning."""

from merakiwrapper import MerakiWrapper
from registereddevicesloader import RegisteredDevicesLoader
from merakiactiveclientsloader import MerakiActiveClientsLoader
from merakifixedipreservationsloader import MerakiFixedIpReservationsLoader
from devicetableloader import DeviceTableLoader

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

    def show_devices(self,df,msg) :
        print(f'{df.shape[0]} {msg}:')
        for name in df['name']:
            print(f'     {name}')

    def report(self) :
        df = self.device_table.df
        unregistered_df = df.loc[(df['registered'] == False)]
        self.show_devices(unregistered_df, 'unregistered devices:')
        registered_df = df.loc[(df['registered'])] 
        self.show_devices(registered_df, 'registered devices:')
        no_fixed_ip_reservation_df = df.loc[(df['reserved'] == False)]
        self.show_devices(no_fixed_ip_reservation_df, 'devices do not have a fixed IP reservation:')
        has_fixed_ip_reservation_df = df.loc[(df['reserved'])]
        self.show_devices(has_fixed_ip_reservation_df , 'devices have a fixed IP reservation:')
        inactive_df = df.loc[(df['active'] == False)]
        self.show_devices(inactive_df, 'devices are inactive:')
        is_active_df = df.loc[(df['active'])]
        self.show_devices(is_active_df, 'devices are active:')

