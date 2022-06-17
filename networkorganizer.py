import os.path
import getpass
from pandas import DataFrame
from merakinetworkmapper import MerakiNetworkMapper
from registereddevicesloader import RegisteredDevicesLoader
from devicetableloader import DeviceTableLoader
from registereddevicesgenerator import RegisteredDevicesGenerator
from merakiactiveclientsloader import MerakiActiveClientsLoader
from merakifixedipreservationsloader import MerakiFixedIpReservationsLoader
from merakiwrapper import MerakiWrapper

class NetworkOrganizerException(Exception) :
    pass

def get_api_key() : 
    print ("You will need to obtain an API key. See the following for details:") 
    print ("https://developer.cisco.com/meraki/api-v1/#!authorization/obtaining-your-meraki-api-key") 
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

meraki_wrapper = MerakiWrapper(get_api_key(),choose_from_options) 
registered_devices_loader = RegisteredDevicesLoader()
meraki_active_clients_loader = MerakiActiveClientsLoader(
    meraki_wrapper.dashboard,
    meraki_wrapper.serial_id,
    meraki_wrapper.vlan_id)
meraki_fixed_ip_reservations_loader = MerakiFixedIpReservationsLoader(
    meraki_wrapper.dashboard,
    meraki_wrapper.network_id,
    meraki_wrapper.vlan_id)
device_table_loader = DeviceTableLoader(
    registered_devices_loader,
    meraki_active_clients_loader,
    meraki_fixed_ip_reservations_loader)
device_table = device_table_loader.load_all() 

# Generate devices.yml
registered_devices_generator = RegisteredDevicesGenerator() 
print(registered_devices_generator.generate(device_table))
df = device_table.df
print(df)

# Map devices to the network space

meraki_network_mapper = MerakiNetworkMapper(device_table,meraki_wrapper)
meraki_network_mapper.map_devices_to_network_space()

#print(df.query("registered and reserved"))
#unregistered_df = df.loc[(df['registered'] == False)]
#no_fixed_ip_reservation_df = df.loc[(df['reserved'] == False)]
#inactive_df = df.loc[(df['active'] == False)]
#registered_df = df.loc[(df['registered'])] 
#has_fixed_ip_reservation_df = df.loc[(df['reserved'])]
#is_active_df = df.loc[(df['active'])]
#print(f'{df.shape[0]} devices')
#print(f'{registered_df.shape[0]} registered devices')
#print(f'{unregistered_df.shape[0]} unregistered devices')
#print(f'{has_fixed_ip_reservation_df.shape[0]} devices have a fixed IP reservation')
#print(f'{no_fixed_ip_reservation_df.shape[0]} devices do not have a fixed IP reservation')
#print(f'{is_active_df.shape[0]} devices are active')
#print(f'{inactive_df.shape[0]} devices are not active')