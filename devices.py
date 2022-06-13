import yaml

class Devices:
        
    def __init__(self) :
        self.device_list = []

    def get_device_list(self):
        return self.device_list

    def load(self,filename):
        with open(filename) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            devices = data['devices']
            device_group_names = devices.keys()
            for device_group_name in device_group_names:
                devices_in_group = devices[device_group_name] 
                for device_in_group in devices_in_group: 
                    s = device_in_group.split(',') 
                    device_name = s[0] 
                    device_mac = s[1] 
                    device = {'name': device_name, 'mac': device_mac, 'group': device_group_name}
                    self.device_list.append(device)

