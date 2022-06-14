import os.path
import getpass
from pandas import DataFrame
from devicetable import DeviceTableBuilder
from devices import Devices
from merakiwrapper import MerakiWrapper, MerakiWrapperException

class DeviceTableLoaderException(Exception) :
    pass

class DeviceTableLoader :

    def get_api_key() : 
        print ("You will need to obtain an API key. See the following for details:") 
        print ("https://developer.cisco.com/meraki/api-v1/#!authorization/obtaining-your-meraki-api-key") 
        #api_key = input("Meraki API key: ") 
        api_key = getpass.getpass('Meraki API key: ')
        return api_key

    def choose_from_options(thing, choices) :
        print(f'Multiple {thing}s found:')
        [ print(f'{k} - {v}') for (k,v) in choices.items()]
        while True: 
            selection = input(f'Which {thing}? : ') 
            if selection in choices:
                break
        return selection

    def __init__(self) -> None:
        self.device_table_builder = DeviceTableBuilder() 
        try:
            self.meraki_wrapper = MerakiWrapper(DeviceTableLoader.get_api_key(),DeviceTableLoader.choose_from_options) 
        except MerakiWrapperException as exc:
            print(f'Failed to initialize DeviceTableLoader')
            raise DeviceTableLoaderException from exc

    def load_classified(self,devices_yaml="devices.yml") -> None:
        devices = Devices() 
        if os.path.exists(devices_yaml) : 
            print(f'Loading devices from {devices_yaml}')
            devices.load(devices_yaml)
            for device in devices.get_device_list() : 
                # All we know at this point is the device is classified
                record = DeviceTableBuilder.generate_new_record()
                record['classified'] = True
                record['group'] = device['group'] 
                record['name'] = device['name']
                self.device_table_builder.set_details(device['mac'], record)
        else :
            print(f'{devices_yaml} not found')

    def load_active_clients(self) : 
        active_clients = self.meraki_wrapper.get_device_clients_for_vlan()
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
                print(f'Creating record for unclassified {record["name"]} {active_client["mac"]}')
                self.device_table_builder.set_details(active_client['mac'], record)

    def load_fixed_ip_reservations(self) :
        fixed_ip_reservations = self.meraki_wrapper.get_existing_reservatons()
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
        try:
            self.load_classified()
            self.load_active_clients()
            self.load_fixed_ip_reservations()
            device_table = self.device_table_builder.build()
            if device_table.is_valid() :
                print("device table is valid")
                return device_table.df
            else :
                print("device table is invalid") 
                return device_table.df
        except MerakiWrapperException as exc:
            raise DeviceTableLoaderException from exc