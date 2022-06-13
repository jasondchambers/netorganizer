import meraki

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

    def get_org_id(dashboard) :
        organizations= dashboard.organizations.getOrganizations() 
        if len(organizations) == 0 : 
            raise NoOrganizationFound
        elif len(organizations) > 1 : 
            raise MoreThanOneOrganizationFound
        return organizations[0]["id"]

    def build_choices(menu) :
        choice = 1
        choices = dict()
        for network_name in menu:
            choices[str(choice)] = network_name
            choice += 1
        return choices

    def select_from_networks(networks, chooser_func) :
        network_names = [network['name'] for network in networks]
        choices = MerakiWrapper.build_choices(network_names)
        selection = chooser_func("network",choices)
        return networks[int(selection)-1]["id"]

    def select_from_devices(devices, chooser_func) :
        device_names = [ f'{device["model"]} - {device["serial"]}' for device in devices]
        choices = MerakiWrapper.build_choices(device_names)
        selection = chooser_func("device",choices)
        return devices[int(selection)-1]["serial"]

    def select_from_vlans(vlans, chooser_func) :
        vlan_names = [ f'{vlan["name"]} - {vlan["subnet"]}' for vlan in vlans]
        choices = MerakiWrapper.build_choices(vlan_names)
        selection = chooser_func("VLAN",choices)
        return vlans[int(selection)-1]["id"]

    def get_network_id(dashboard, org_id, chooser_func) :
        networks = dashboard.organizations.getOrganizationNetworks(org_id)
        if len(networks) == 0 :
            raise NoNetworksFound
        elif len(networks) > 1 :
            return MerakiWrapper.select_from_networks(networks, chooser_func)
        return networks[0]["id"]

    def get_device_serial_id(dashboard, network_id, chooser_func) :
        devices = dashboard.networks.getNetworkDevices(network_id)
        if len(devices) == 0 :
            raise NoDevicesFound
        elif len(devices) > 1 :
            return MerakiWrapper.select_from_devices(devices, chooser_func)
        return devices[0]["serial"]

    def get_vlan_id(dashboard, network_id, chooser_func) :
        vlans = dashboard.appliance.getNetworkApplianceVlans(network_id)
        if len(vlans) == 0 :
            raise NoVlansFound
        elif len(vlans) > 1 :
            return MerakiWrapper.select_from_vlans(vlans, chooser_func)
        return vlans[0]["id"]

    def get_vlan_subnet(dashboard,network_id,vlan_id) :
        vlan = dashboard.appliance.getNetworkApplianceVlan(network_id, vlan_id)
        return vlan['subnet']

    def get_device_clients(self) :
        device_clients = self.dashboard.devices.getDeviceClients(self.serial_id)
        return device_clients

    def get_device_clients_for_vlan(self) :
        device_clients = self.get_device_clients()
        filtered_for_vlan = [ device_client for device_client in device_clients if device_client['vlan'] == self.vlan_id]
        return filtered_for_vlan

    def get_vlan(self) : 
        vlan = self.dashboard.appliance.getNetworkApplianceVlan(self.network_id, self.vlan_id)
        return vlan

    def get_existing_reservatons(self) :
        vlan = self.get_vlan()
        existing_reservations = vlan['fixedIpAssignments']
        return existing_reservations

    def __init__(self, api_key, chooser_func) : 
        print("Validating API key...") 
        if not api_key : raise InvalidApiKey 
        self.dashboard = meraki.DashboardAPI(api_key, suppress_logging=True) 
        try : 
            self.org_id = MerakiWrapper.get_org_id(self.dashboard)
            self.network_id = MerakiWrapper.get_network_id(self.dashboard, self.org_id, chooser_func)
            self.serial_id = MerakiWrapper.get_device_serial_id(self.dashboard, self.network_id, chooser_func)
            self.vlan_id = MerakiWrapper.get_vlan_id(self.dashboard, self.network_id, chooser_func)
            self.vlan_subnet = MerakiWrapper.get_vlan_subnet(self.dashboard,self.network_id,self.vlan_id)
        except meraki.exceptions.APIError as exc:
            print(f'Failed to initialize MerakiWrapper: {exc}')
            raise MerakiWrapperException from exc