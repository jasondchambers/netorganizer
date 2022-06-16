
class MerakiActiveClientsLoader:
    
    def __init__(self,meraki_dashboard,serial_id, vlan_id) -> None:
        self.dashboard = meraki_dashboard
        self.serial_id = serial_id
        self.vlan_id = vlan_id

    def load(self) :
        device_clients = self.dashboard.devices.getDeviceClients(self.serial_id)
        filtered_for_vlan = [ device_client for device_client in device_clients if device_client['vlan'] == self.vlan_id]
        return filtered_for_vlan