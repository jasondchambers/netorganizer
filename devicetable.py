"""All the things associated with Loading, building and accessing a device table."""
import pandas as pd
from pandas import DataFrame

class DeviceTable :
    """The device table is the heart of Network Organizer."""
    def __init__(self,data) -> None:
        # pylint: disable=invalid-name
        self.df = pd.DataFrame(data)

class DeviceTableBuilder :
    """Efficiently Build a DeviceTable."""
    def __init__(self) -> None:
        self.devices_dict = {}

    @staticmethod
    def generate_new_record() -> dict:
        """Generate a new record with default values."""
        return {
            'known': False,
            'reserved': False,
            'active': False,
            'ip': '',
            'group': 'unclassified',
            'name': ''}

    def get_details(self,mac) -> dict:
        """For a given device identified by it's MAC, return the details."""
        if mac in self.devices_dict:
            return self.devices_dict[mac]
        self.devices_dict[mac] = {}
        return self.devices_dict[mac]

    def set_details(self,mac,details) -> None:
        """Set the details for a given device identified by it's MAC."""
        self.devices_dict[mac] = details

    def build(self) -> DeviceTable:
        """Build the DeviceTable."""
        data = []
        # pylint: disable=consider-using-dict-items
        for mac in self.devices_dict:
            details = self.devices_dict[mac]
            device_mac_dict = {'mac': mac}
            merged = {**device_mac_dict,**details}
            data.append(merged)
        return DeviceTable(data)

class DeviceTableLoader :
    """Load data into the DeviceTable."""

    def __init__(self,known_devices_loader,active_clients_loader,
                 fixed_ip_reservations_loader) -> None:
        self.device_table_builder = DeviceTableBuilder()
        self.known_devices_loader = known_devices_loader
        self.active_clients_loader = active_clients_loader
        self.fixed_ip_reservations_loader = fixed_ip_reservations_loader

    def load_known(self) -> None:
        """Load known devices into the DeviceTable."""
        known_devices = self.known_devices_loader.load()
        for device in known_devices :
            # All we know at this point is the device is known
            record = DeviceTableBuilder.generate_new_record()
            record['known'] = True
            record['group'] = device['group']
            record['name'] = device['name']
            self.device_table_builder.set_details(device['mac'], record)

    def load_active_clients(self) :
        """Load active clients into the DeviceTable."""
        active_clients = self.active_clients_loader.load()
        for active_client in active_clients :
            record = self.device_table_builder.get_details(active_client['mac'])
            if record:
                # device has been loaded already
                record['active'] = True
                record['ip'] = active_client['ip']
                self.device_table_builder.set_details(active_client['mac'], record)
            else:
                # Seeing device for the first time
                record = DeviceTableBuilder.generate_new_record()
                record['active'] = True
                record['ip'] = active_client['ip']
                record['name'] = active_client['description']
                self.device_table_builder.set_details(active_client['mac'], record)

    def load_fixed_ip_reservations(self) :
        """Load fixed IP reservations into the DeviceTable."""
        # pylint: disable=line-too-long
        fixed_ip_reservations = self.fixed_ip_reservations_loader.load()
        if fixed_ip_reservations:
            for mac, fixed_ip_reservation_details in fixed_ip_reservations.items():
                record = self.device_table_builder.get_details(mac)
                if record:
                    record['reserved'] = True
                    if record['ip']:
                        if record['ip'] != fixed_ip_reservation_details['ip']:
                            print(f'DeviceTableLoader: for {record["name"]} reservation {fixed_ip_reservation_details["ip"]} differs to current lease {record["ip"]}')
                            print(f'DeviceTableLoader: using current lease {record["ip"]} to avoid potential for collisions')
                    if record['active'] is False :
                        # Is in-active - has no IP so use the reserved IP
                        record['ip'] = fixed_ip_reservation_details['ip']
                    self.device_table_builder.set_details(mac, record)
                else :
                    # Seeing device for the first time
                    record = DeviceTableBuilder.generate_new_record()
                    record['reserved'] = True
                    record['ip'] = fixed_ip_reservation_details['ip']
                    record['name'] = fixed_ip_reservation_details['name']
                    self.device_table_builder.set_details(mac, record)

    def load_all(self) -> DataFrame :
        """Load everything into the DeviceTable."""
        self.load_known()
        self.load_active_clients()
        self.load_fixed_ip_reservations()
        return self.device_table_builder.build()
