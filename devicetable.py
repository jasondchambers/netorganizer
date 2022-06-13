import pandas as pd

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

    def has_unique_names(self) -> bool:
        if len(self.df.name.unique() == self.df.shape[0]) :
            return True 
        else :
            print('Duplicate names in device table')
            return False

    def is_valid(self) :
        v = self.has_unique_macs() and self.has_unique_ips() and self.has_unique_names()
        return v
        
class DeviceTableBuilder :
    def __init__(self) -> None:
        self.devices_dict = dict()
        
    def get_details(self,mac) -> set:
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
            data.append(s | details)
        return DeviceTable(data)
        