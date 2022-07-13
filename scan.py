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
        self.analysis = {
            'not_registered_not_reserved_ACTIVE': {
                'query': 'not registered and not reserved and active',
                'device_names': [],
                'action': 'New device(s)? These will be registered as un-classified during the next organize'
            },
            'not_registered_RESERVED_not_active': {
                'query': 'not registered and reserved and not active',
                'device_names': [],
                'action': 'Retired device(s)? The reserved IP will be removed during the next organize'
            },
            'not_registered_RESERVED_ACTIVE': {
                'query': 'not registered and reserved and active',
                'device_names': [],
                'action': 'These will be registered as un-classified during the next organize'
            },
            'REGISTERED_not_reserved_not_active': {
                'query': 'registered and not reserved and not active',
                'device_names': [],
                'action': 'A reserved IP will be created during the next organize'
            },
            'REGISTERED_not_reserved_ACTIVE': {
                'query': 'registered and not reserved and active',
                'device_names': [],
                'action': 'The current IP will be converted to a static IP during the next organize'
            },
            'REGISTERED_RESERVED_not_active': {
                'query': 'registered and reserved and not active',
                'device_names': [],
                'action': 'These devices are currently inactive - no action will be taken during the next organize'
            },
            'REGISTERED_RESERVED_ACTIVE': {
                'query': 'registered and reserved and active',
                'device_names': [],
                'action': 'Normal state - no action will be taken during the next organize'
            },
            'ACTIVE_UNCLASSIFIED': {
                'query': "active and group == 'unclassified'",
                'device_names': [],
                'action': 'You should consider classifying them before the next organize'
            }
        }

    def run(self):
        df = self.device_table.df
        for k, v in self.analysis.items():
            query_result_df = df.query(v['query'])
            v['device_names'] = query_result_df['name'].values.tolist()

    def report(self) :
        df = self.device_table.df
        for k, v in self.analysis.items():
            if len(v["device_names"]) == 0:
                print(f'Did not find any devices that are: {v["query"]}') 
            else:
                print(f'Found {len(v["device_names"])} device(s) that are: {v["query"]}') 
                print(f'{v["action"]}')
                for device_name in v['device_names']:
                    print(f'     {device_name}')