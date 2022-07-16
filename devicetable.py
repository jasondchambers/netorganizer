import pandas as pd
from pandas import DataFrame

class DeviceTable :
    def __init__(self,data) -> None:
        self.df = pd.DataFrame(data)

    def has_unique_macs(self) -> bool:
        if len(self.df.mac.unique() == self.df.shape[0]) :
            return True 
        else :
            print('Duplicate MACs in device table')
            return False

    def has_unique_ips(self) -> bool:
        if len(self.df.ip.unique() == self.df.shape[0]) :
            return True 
        else :
            print('Duplicate IPs in device table')
            return False

class DeviceTableBuilder :
    def __init__(self) -> None:
        self.devices_dict = dict()
        
    def generate_new_record() -> dict:
        return { 
            'known': False, 
            'reserved': False, 
            'active': False, 
            'ip': '', 
            'group': 'unclassified', 
            'name': ''}

    def get_details(self,mac) -> dict:
        if mac in self.devices_dict:
            return self.devices_dict[mac]
        else:
            self.devices_dict[mac] = {}
            return self.devices_dict[mac]
            
    def set_details(self,mac,details) -> None:
        self.devices_dict[mac] = details
        
    def build(self) -> DeviceTable:
        data = []
        for mac in self.devices_dict:
            details = self.devices_dict[mac]
            s = {'mac': mac}
            #data.append(s | details)
            merged = {**s,**details}
            data.append(merged)
        return DeviceTable(data)
        
class DeviceTableLoaderException(Exception) :
    pass

class DeviceTableLoader :

    def __init__(self,known_devices_loader,active_clients_loader,fixed_ip_reservations_loader) -> None:
        self.device_table_builder = DeviceTableBuilder() 
        self.known_devices_loader = known_devices_loader
        self.active_clients_loader = active_clients_loader
        self.fixed_ip_reservations_loader = fixed_ip_reservations_loader


    def load_known(self) -> None:
        known_devices = self.known_devices_loader.load()
        for device in known_devices :
            # All we know at this point is the device is known
            record = DeviceTableBuilder.generate_new_record()
            record['known'] = True
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
                self.device_table_builder.set_details(active_client['mac'], record)
            else:
                # Seeing device for the first time
                record = DeviceTableBuilder.generate_new_record()
                record['active'] = True 
                record['ip'] = active_client['ip']
                record['name'] = active_client['description']
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
                    self.device_table_builder.set_details(mac, record)
                else :
                    # Seeing device for the first time
                    record = DeviceTableBuilder.generate_new_record()
                    record['reserved'] = True
                    record['ip'] = fixed_ip_reservation_details['ip']
                    record['name'] = fixed_ip_reservation_details['name']
                    self.device_table_builder.set_details(mac, record)

    def load_all(self) -> DataFrame :
        self.load_known()
        self.load_active_clients()
        self.load_fixed_ip_reservations()
        return self.device_table_builder.build()
