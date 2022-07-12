"""This is the main module for Netorg generate."""

from netorgmeraki import MerakiWrapper, MerakiActiveClientsLoader, MerakiFixedIpReservationsLoader
from registereddevicesloader import RegisteredDevicesLoader
from devicetable import DeviceTableLoader

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


class RegisteredDevicesGenerator:

    def get_devices_in_group(self,df,group) -> list :
        l = []
        for index, row in df.query(f'group == "{group}"').iterrows(): 
            l.append(f'{row["name"]},{row["mac"]}')
        return l

    def get_groups(self,df) -> list :
        return df.group.unique().tolist()

    def generate(self,device_table) -> str :
        yaml_lines = []
        yaml_lines.append("devices:")
        df = device_table.df
        groups = self.get_groups(df)
        for group_name in groups :
            if group_name == "" : 
                # Classify unregistered devices as unclassified
                yaml_lines.append("  unclassified:")
            else : 
                yaml_lines.append(f'  {group_name}:')
            devices_in_group = self.get_devices_in_group(df,group_name)
            for device_in_group in devices_in_group : 
                yaml_lines.append(f'    - {device_in_group}')
        s = '\n'.join(yaml_lines)
        return s