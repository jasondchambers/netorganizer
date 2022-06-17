import os.path
import yaml

class RegisteredDevicesLoader:
        
    def load(self,filename='./devices.yml') -> list:
        device_list = [] 
        if os.path.exists(filename) : 
            print(f'Loading registered devices from {filename}') 
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
                        device_list.append(device)
        else:
            print(f'{filename} not found') 
        return device_list

