from devicetableloader import DeviceTableLoader
from ports import ActiveClientsPort, DeviceTableCsvOutPort, FixedIpReservationsPort, KnownDevicesPort, SecureNetworkAnalyticsHostGroupManagementPort
from scan import NetorgScanner

class NetOrganizerApp():

    def __init__(self, 
                 known_devices_port: KnownDevicesPort,
                 active_clients_port: ActiveClientsPort,
                 fixed_ip_reservations_port: FixedIpReservationsPort,
                 device_table_csv_out_port: DeviceTableCsvOutPort,
                 sna_hostgroup_port: SecureNetworkAnalyticsHostGroupManagementPort) -> None:
        self.known_devices_port = known_devices_port
        self.active_clients_port = active_clients_port
        self.fixed_ip_reservations_port = fixed_ip_reservations_port 
        self.device_table_csv_out_port = device_table_csv_out_port
        self.sna_hostgroup_port = sna_hostgroup_port 

    def do_devicetable(self) -> None:
        device_table = self.__load_device_table()
        self.device_table_csv_out_port.write(device_table.df.to_csv())

    def do_scan(self) -> None:
        device_table = self.__load_device_table()
        scanner = NetorgScanner(device_table)
        scanner.run()
        #TODO - change to a port
        scanner.report()

    def do_save_known_devices(self) -> None:
        device_table = self.__load_device_table()
        self.known_devices_port.save(device_table)

    def do_organize(self) -> None:
        device_table = self.__load_device_table() 
        self.known_devices_port.save(device_table)
        self.fixed_ip_reservations_port.save(device_table)

    def do_push_changes_to_sna(self) -> None:
        device_table = self.__load_device_table() 
        # Ensure things are organized before we push changes to SNA
        # Mostly this is to ensure devices have IPs
        self.known_devices_port.save(device_table)
        self.fixed_ip_reservations_port.save(device_table) 
        self.sna_hostgroup_port.update_host_groups(device_table)

    def __load_device_table(self):
        """Load the device table."""
        device_table_loader = DeviceTableLoader(
            self.known_devices_port,
            self.active_clients_port,
            self.fixed_ip_reservations_port)
        return device_table_loader.load_all()