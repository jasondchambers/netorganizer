from pandas import DataFrame
from devicetableloader import DeviceTableLoader, DeviceTableLoaderException

class NetworkOrganizerException(Exception) :
    pass

#
#    classified | existing reservation | existing client | Description                         | Action
# ==============+======================+=================+=====================================+=======
#             0 |                    0 |               0 | Unclassified & unreserved & inactive| N/A
# aab         0 |                    0 |               1 | Unclassified & unreserved & active  | Ask user to classify 
# aba         0 |                    1 |               0 | Unclassified & reserved & inactive  | Remove reservation
# abb         0 |                    1 |               1 | Unclassified & reserved & active    | Ask user to classify
# baa         1 |                    0 |               0 | Classified & unreserved & inactive  | Create reservation
# bab         1 |                    0 |               1 | Classified & unreserved & active    | Convert to static reservation
# bba         1 |                    1 |               0 | Classified & reserved & inactive    | No change
# bbb         1 |                    1 |               1 | Classified & reserved & active      | No change

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
