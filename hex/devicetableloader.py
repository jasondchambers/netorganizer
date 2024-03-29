
from ports import ActiveClientsPort, FixedIpReservationsPort, KnownDevicesPort
from devicetable import DeviceTable

class DeviceTableBuilder :
    """Efficiently Build a DeviceTable."""
    def __init__(self) -> None:
        self.__devices_dict = {}

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
        if mac in self.__devices_dict:
            return self.__devices_dict[mac]
        self.__devices_dict[mac] = {}
        return self.__devices_dict[mac]

    def set_details(self,mac,details) -> None:
        """Set the details for a given device identified by it's MAC."""
        self.__devices_dict[mac] = details

    def build(self) -> DeviceTable:
        """Build the DeviceTable."""
        data = []
        # pylint: disable=consider-using-dict-items
        for mac in self.__devices_dict:
            details = self.__devices_dict[mac]
            device_mac_dict = {'mac': mac}
            merged = {**device_mac_dict,**details}
            data.append(merged)
        return DeviceTable(data)

class DeviceTableLoader :
    """Load data into the DeviceTable."""

    def __init__(self, 
                 known_devices_port: KnownDevicesPort, 
                 active_clients_port: ActiveClientsPort,
                 fixed_ip_reservations_port: FixedIpReservationsPort) -> None:
        self.device_table_builder = DeviceTableBuilder()
        self.known_devices_port = known_devices_port
        self.active_clients_port = active_clients_port
        self.fixed_ip_reservations_port = fixed_ip_reservations_port

    def load_all(self) -> DeviceTable :
        """Load everything into the DeviceTable."""
        self.__load_known()
        self.__load_active_clients()
        self.__load_fixed_ip_reservations()
        return self.device_table_builder.build()

    def __load_known(self) -> None:
        """Load known devices into the DeviceTable."""
        known_devices = self.known_devices_port.load()
        for known_device in known_devices :
            # All we know at this point is the device is known
            record = DeviceTableBuilder.generate_new_record()
            record['known'] = True
            record['group'] = known_device.group
            record['name'] = known_device.name
            self.device_table_builder.set_details(known_device.mac, record)

    def __load_active_clients(self) -> None:
        """Load active clients into the DeviceTable."""
        active_clients = self.active_clients_port.load()
        for active_client in active_clients :
            record = self.device_table_builder.get_details(active_client.mac)
            if record:
                # device has been loaded already
                record['active'] = True
                record['ip'] = active_client.ip_address
                self.device_table_builder.set_details(active_client.mac, record)
            else:
                # Seeing device for the first time
                record = DeviceTableBuilder.generate_new_record()
                record['active'] = True
                record['ip'] = active_client.ip_address
                record['name'] = active_client.description
                self.device_table_builder.set_details(active_client.mac, record)

    def __load_fixed_ip_reservations(self) -> None:
        """Load fixed IP reservations into the DeviceTable."""
        # pylint: disable=line-too-long
        fixed_ip_reservations = self.fixed_ip_reservations_port.load()
        if fixed_ip_reservations:
            #for mac, fixed_ip_reservation_details in fixed_ip_reservations.items():
            for fixed_ip_reservation in fixed_ip_reservations:
                record = self.device_table_builder.get_details(fixed_ip_reservation.mac)
                if record:
                    record['reserved'] = True
                    if record['ip']:
                        if record['ip'] != fixed_ip_reservation.ip_address:
                            print(f'DeviceTableLoader: for {record["name"]} reservation {fixed_ip_reservation.ip_address} differs to current lease {record["ip"]}')
                            print(f'DeviceTableLoader: using current lease {record["ip"]} to avoid potential for collisions')
                    if record['active'] is False :
                        # Is in-active - has no IP so use the reserved IP
                        record['ip'] = fixed_ip_reservation.ip_address
                    self.device_table_builder.set_details(fixed_ip_reservation.mac, record)
                else :
                    # Seeing device for the first time
                    record = DeviceTableBuilder.generate_new_record()
                    record['reserved'] = True
                    record['ip'] = fixed_ip_reservation.ip_address
                    record['name'] = fixed_ip_reservation.name
                    self.device_table_builder.set_details(fixed_ip_reservation.mac, record)
