"""This is the main module for Netorg generate."""

class NetorgGenerator:
    """All things associated with Netorg generate"""

    def __init__(self, config, device_table):
        self.device_table = device_table
        self.devices_yml_path = config['devices_yml']

    def generate(self) :
        known_devices_generator = KnownDevicesGenerator() 
        print(f'Generating devices.yml file at {self.devices_yml_path}')
        with open(self.devices_yml_path, 'w', encoding='utf8') as devices_yml_file:
            devices_yml_file.write(known_devices_generator.generate(self.device_table))


class KnownDevicesGenerator:

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
                # Classify unknown devices as unclassified
                yaml_lines.append("  unclassified:")
            else : 
                yaml_lines.append(f'  {group_name}:')
            devices_in_group = self.get_devices_in_group(df,group_name)
            for device_in_group in devices_in_group : 
                yaml_lines.append(f'    - {device_in_group}')
        s = '\n'.join(yaml_lines)
        return s