from devicetable import DeviceTable, DeviceTableBuilder

class RegisteredDevicesGenerator:

    def get_devices_in_group(self,df,group) -> list :
        l = []
        for index, row in df.query(f'group == "{group}"').iterrows(): 
            l.append(f'{row["name"]},{row["mac"]}')
        return l

    def get_groups(self,df) -> list :
        return df.group.unique().tolist()

    def generate(self,device_table) -> str :
        yaml_lines = []
        yaml_lines.append("devices:")
        df = device_table.df
        groups = self.get_groups(df)
        for group_name in groups :
            if group_name == "" : 
                # Classify unregistered devices as unclassified
                yaml_lines.append("  unclassified:")
            else : 
                yaml_lines.append(f'  {group_name}:')
            devices_in_group = self.get_devices_in_group(df,group_name)
            for device_in_group in devices_in_group : 
                yaml_lines.append(f'    - {device_in_group}')
        s = '\n'.join(yaml_lines)
        return s