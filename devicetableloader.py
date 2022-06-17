from pandas import DataFrame
from devicetable import DeviceTableBuilder

class DeviceTableLoaderException(Exception) :
    pass

class DeviceTableLoader :

    def __init__(self,registered_devices_loader,active_clients_loader,fixed_ip_reservations_loader) -> None:
        self.device_table_builder = DeviceTableBuilder() 
        self.registered_devices_loader = registered_devices_loader
        self.active_clients_loader = active_clients_loader
        self.fixed_ip_reservations_loader = fixed_ip_reservations_loader


    def load_registered(self) -> None:
        registered_devices = self.registered_devices_loader.load()
        for device in registered_devices :
            # All we know at this point is the device is registered
            record = DeviceTableBuilder.generate_new_record()
            record['registered'] = True
            record['group'] = device['group'] 
            record['name'] = device['name']
            self.device_table_builder.set_details(device['mac'], record)

    def load_active_clients(self) : 
        active_clients = self.active_clients_loader.load() 
        for active_client in active_clients :
            record = self.device_table_builder.get_details(active_client['mac'])
            if record:
                # device has been loaded already
                record['active'] = True
                record['ip'] = active_client['ip'] 
                print(f'Updating record ip and active for {record["name"]} {active_client["mac"]}')
                self.device_table_builder.set_details(active_client['mac'], record)
            else:
                # Seeing device for the first time
                record = DeviceTableBuilder.generate_new_record()
                record['active'] = True 
                record['ip'] = active_client['ip']
                record['name'] = active_client['description']
                print(f'Creating record for unregistered {record["name"]} {active_client["mac"]}')
                self.device_table_builder.set_details(active_client['mac'], record)

    def load_fixed_ip_reservations(self) :
        fixed_ip_reservations = self.fixed_ip_reservations_loader.load()
        if fixed_ip_reservations:
            for mac, fixed_ip_reservation_details in fixed_ip_reservations.items():
                record = self.device_table_builder.get_details(mac)
                if record:
                    record['reserved'] = True
                    if (record['active'] == False) :
                        # Is in-active - has no IP so use the reserved IP
                        record['ip'] = fixed_ip_reservation_details['ip']
                    print(f'Updating record reserved for {record["name"]} {mac}')
                    self.device_table_builder.set_details(mac, record)
                else :
                    # Seeing device for the first time
                    record = DeviceTableBuilder.generate_new_record()
                    record['reserved'] = True
                    record['ip'] = fixed_ip_reservation_details['ip']
                    record['name'] = fixed_ip_reservation_details['name']
                    print(f'Creating record ip reserved for {record["name"]} {mac}')
                    self.device_table_builder.set_details(mac, record)

    def load_all(self) -> DataFrame :
        self.load_registered()
        self.load_active_clients()
        self.load_fixed_ip_reservations()
        device_table = self.device_table_builder.build()
        if device_table.is_valid() :
            print("device table is valid")
            return device_table.df
        else :
            print("device table is invalid") 
            return device_table.df