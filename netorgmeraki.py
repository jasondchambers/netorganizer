import meraki
import re
from deepdiff import DeepDiff
from ipv4privatenetworkspace import Ipv4PrivateNetworkSpace

class MerakiWrapperException(Exception) :
    pass

class InvalidApiKey(MerakiWrapperException) :
    pass

class FailedToInitializeMeraki(MerakiWrapperException) :
    pass

class NoOrganizationFound(MerakiWrapperException) :
    pass

class MoreThanOneOrganizationFound(MerakiWrapperException) :
    pass

class NoNetworksFound(MerakiWrapperException) :
    pass

class NoDevicesFound(MerakiWrapperException) :
    pass

class NoVlansFound(MerakiWrapperException) :
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
        elif len(organizations) > 1 : 
            raise MoreThanOneOrganizationFound
        return organizations[0]["id"]

    @staticmethod
    def build_choices(menu) -> dict:
        """Build a choices dict where each menu item has a numeric key"""
        choice = 1
        choices = dict()
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
        elif len(devices) > 1 :
            return MerakiWrapper.select_from_devices(devices, chooser_func)
        return devices[0]["serial"]

    @staticmethod
    def find_vlan_id(dashboard, network_id, chooser_func) -> str:
        """Return the VLAN id."""
        vlans = dashboard.appliance.getNetworkApplianceVlans(network_id)
        if len(vlans) == 0 :
            raise NoVlansFound
        elif len(vlans) > 1 :
            return MerakiWrapper.select_from_vlans(vlans, chooser_func)
        return vlans[0]["id"]

    @staticmethod
    def find_vlan_subnet(dashboard,network_id,vlan_id) -> str:
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
            self.network_id = MerakiWrapper.find_network_id(self.dashboard, self.org_id, chooser_func)
            self.serial_id = MerakiWrapper.find_device_serial_id(self.dashboard, self.network_id, chooser_func)
            self.vlan_id = MerakiWrapper.find_vlan_id(self.dashboard, self.network_id, chooser_func)
            self.vlan_subnet = MerakiWrapper.find_vlan_subnet(self.dashboard,self.network_id,self.vlan_id)
        except meraki.exceptions.APIError as exc:
            print(f'Failed to initialize MerakiWrapper: {exc}')
            raise MerakiWrapperException from exc



class MerakiActiveClientsLoader:
    
    def __init__(self,meraki_dashboard,serial_id, vlan_id) -> None:
        self.dashboard = meraki_dashboard
        self.serial_id = serial_id
        self.vlan_id = vlan_id

    def load(self) :
        device_clients = self.dashboard.devices.getDeviceClients(self.serial_id)
        filtered_for_vlan = [ device_client for device_client in device_clients if device_client['vlan'] == self.vlan_id]
        return filtered_for_vlan



class MerakiFixedIpReservationsGenerator : 
    def generate(self,device_table) -> dict:
        dict = {}
        df = device_table.df
        skip_these_macs = df.query("not known and reserved and not active").mac.unique().tolist()
        macs = df.mac.unique().tolist()
        for mac in macs :
            if mac not in skip_these_macs: 
                device_df = df.query('mac == @mac') 
                if device_df.shape[0] == 1: 
                    ip = device_df.iloc[0]['ip'] 
                    name = device_df.iloc[0]['name'] 
                    dict[mac] = { 
                        'ip': ip, 
                        'name': name
                    }
            else:
                print(f'MerakiFixedIpReservationsGenerator: skipping {mac}')
        return dict

class MerakiFixedIpReservationsLoader:

    def __init__(self,meraki_dashboard,network_id,vlan_id) -> None:
        self.dashboard = meraki_dashboard
        self.network_id = network_id
        self.vlan_id = vlan_id

    def load(self) :
        vlan = self.dashboard.appliance.getNetworkApplianceVlan(self.network_id, str(self.vlan_id))
        existing_reservations = vlan['fixedIpAssignments']
        return existing_reservations

class MerakiNetworkMapper : # TODO

    def __init__(self, config, device_table) -> None:
        self.config = config
        self.device_table = device_table
        self.network_space = Ipv4PrivateNetworkSpace(config['vlan_subnet'])
        for ip in self.find_ips() :
            self.network_space.allocate_specific_address(ip)
        for mac in self.find_macs_needing_ip() :
            self.assign_ip(mac)
    
    def find_ips(self) -> list:
        df = self.device_table.df
        l = df.query("ip != ''")['ip'].tolist() 
        return l

    def find_macs_needing_ip(self) -> list:
        df = self.device_table.df
        l = df.query("ip == ''")['mac'].tolist() 
        return l

    def assign_ip(self,mac) : 
        df = self.device_table.df
        df.loc[df["mac"] == mac, "ip"] = self.network_space.allocate_address()

    def generate_fixed_ip_reservations(self) :
        fixed_ip_reservations_generator = MerakiFixedIpReservationsGenerator()
        return fixed_ip_reservations_generator.generate(self.device_table)

    def show_diffs(self, old_fixed_ip_reservations, new_fixed_ip_reservations):
        diff = DeepDiff(old_fixed_ip_reservations, new_fixed_ip_reservations) 
        if diff:
            print("Fixed IP reservation differences are as follows:") 
            if 'dictionary_item_added' in diff: 
                print("  Adding reservations:")
                added_list = diff['dictionary_item_added'] 
                for added in added_list: 
                    added = re.search("'.*'", added) 
                    if added: 
                        added = added.group() 
                        added = added.strip("'") 
                        print(f'    {new_fixed_ip_reservations[added]["ip"]} for device {added} named {new_fixed_ip_reservations[added]["name"]}')
            else:
                print("  There are no new fixed IP reservations") 
            if 'dictionary_item_removed' in diff: 
                print("  Removing reservations:")
                removed_list = diff['dictionary_item_removed'] 
                for removed in removed_list: 
                    removed = re.search("'.*'", removed) 
                    if removed: 
                        removed = removed.group() 
                        removed = removed.strip("'") 
                        print(f'    {old_fixed_ip_reservations[removed]["ip"]} for device {removed} named {old_fixed_ip_reservations[removed]["name"]}')
        else:
            print("There are no changes to fixed IP reservations")

    def make_fixed_ip_reservations(self) :
        new_fixed_ip_reservations = self.generate_fixed_ip_reservations()
        meraki_wrapper = MerakiWrapper(self.config['api_key'])

        dashboard = meraki_wrapper.dashboard
        network_id = self.config['network_id']
        vlan_id = str(self.config['vlan_id'])

        before_vlan = dashboard.appliance.getNetworkApplianceVlan(network_id, str(vlan_id))
        old_fixed_ip_reservations = before_vlan['fixedIpAssignments']

        self.show_diffs(old_fixed_ip_reservations, new_fixed_ip_reservations) 

        response = dashboard.appliance.updateNetworkApplianceVlan(
            network_id, vlan_id, 
            fixedIpAssignments=new_fixed_ip_reservations)
