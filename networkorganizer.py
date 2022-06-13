from pandas import DataFrame
from devicetableloader import DeviceTableLoader, DeviceTableLoaderException

class NetworkOrganizerException(Exception) :
    pass

class NetworkOrganizer :

    def load_device_table() -> DataFrame : 
        try: 
            device_table_loader = DeviceTableLoader() 
            return device_table_loader.load_all() 
        except DeviceTableLoaderException as exc: 
            print(f'Failed to load device table')
            raise NetworkOrganizerException from exc

    def __init__(self) -> None:
        self.df  = NetworkOrganizer.load_device_table()

try: 
    network_organizer = NetworkOrganizer()
    df = network_organizer.df
    unclassifed_df = df.loc[(df['classified'] == False)]
    no_fixed_ip_reservation_df = df.loc[(df['reserved'] == False)]
    inactive_df = df.loc[(df['active'] == False)]
    classifed_df = df.loc[(df['classified'])] # TODO - fix if no classified hosts/devices.yml
    has_fixed_ip_reservation_df = df.loc[(df['reserved'])]
    is_active_df = df.loc[(df['active'])]
    print(f'{df.shape[0]} devices')
    print(f'{classifed_df.shape[0]} classified devices')
    print(f'{unclassifed_df.shape[0]} unclassified devices')
    print(f'{has_fixed_ip_reservation_df.shape[0]} devices have a fixed IP reservation')
    print(f'{no_fixed_ip_reservation_df.shape[0]} devices do not have a fixed IP reservation')
    print(f'{is_active_df.shape[0]} devices are active')
    print(f'{inactive_df.shape[0]} devices are not active')
except NetworkOrganizerException as exc:
    print(f'Failed to organize network')
