
from typing import List
import meraki
from ports import ActiveClient, ActiveClientsPort

class ActiveClientsMerakiAdapter(ActiveClientsPort):

    def __init__(self, config: dict) -> None:
        self.dashboard = meraki.DashboardAPI(config['api_key'], suppress_logging=True)
        self.serial_id = config['serial_id']
        self.vlan_id   = str(config['vlan_id'])

    # overriding abstract method
    def load(self) -> List[ActiveClient]:
        list_of_active_clients: List[ActiveClient] = []
        device_clients = self.dashboard.devices.getDeviceClients(self.serial_id)
        # pylint: disable=line-too-long
        filtered_for_vlan = [ device_client for device_client in device_clients if device_client['vlan'] == self.vlan_id]
        for device_client in filtered_for_vlan:
            active_client = ActiveClient(
                mac=device_client['mac'],
                name=device_client['dhcpHostname'],
                description=device_client['description'],
                ip_address=device_client['ip']
            )
            list_of_active_clients.append(active_client)
        return list_of_active_clients