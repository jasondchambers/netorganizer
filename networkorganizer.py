import os.path
import getpass
from pandas import DataFrame
from classifieddevicesloader import ClassifiedDevicesLoader
from devicetableloader import DeviceTableLoader, DeviceTableLoaderException
from merakiactiveclientsloader import MerakiActiveClientsLoader
from merakifixedipreservationsloader import MerakiFixedIpReservationsLoader
from merakiwrapper import MerakiWrapper, MerakiWrapperException

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
classified_devices_loader = ClassifiedDevicesLoader()
meraki_active_clients_loader = MerakiActiveClientsLoader(
    meraki_wrapper.dashboard,
    meraki_wrapper.serial_id,
    meraki_wrapper.vlan_id)
meraki_fixed_ip_reservations_loader = MerakiFixedIpReservationsLoader(
    meraki_wrapper.dashboard,
    meraki_wrapper.network_id,
    meraki_wrapper.vlan_id)
device_table_loader = DeviceTableLoader(
    classified_devices_loader,
    meraki_active_clients_loader,
    meraki_fixed_ip_reservations_loader)
df = device_table_loader.load_all() 
print(df.query("classified and reserved"))
unclassifed_df = df.loc[(df['classified'] == False)]
no_fixed_ip_reservation_df = df.loc[(df['reserved'] == False)]
inactive_df = df.loc[(df['active'] == False)]
classifed_df = df.loc[(df['classified'])] 
has_fixed_ip_reservation_df = df.loc[(df['reserved'])]
is_active_df = df.loc[(df['active'])]
print(f'{df.shape[0]} devices')
print(f'{classifed_df.shape[0]} classified devices')
print(f'{unclassifed_df.shape[0]} unclassified devices')
print(f'{has_fixed_ip_reservation_df.shape[0]} devices have a fixed IP reservation')
print(f'{no_fixed_ip_reservation_df.shape[0]} devices do not have a fixed IP reservation')
print(f'{is_active_df.shape[0]} devices are active')
print(f'{inactive_df.shape[0]} devices are not active')