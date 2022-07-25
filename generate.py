"""This is the main module for Netorg generate."""

from deepdiff import DeepDiff
from knowndevicesloader import KnownDevicesLoader

class NetorgGenerator:
    """All things associated with Netorg generate"""

    def __init__(self, config, device_table):
        self.device_table = device_table
        self.devices_yml_path = config['devices_yml']

    @staticmethod
    def show_diffs(old_list, new_list):
        """Show the before and after of the known devices to highlight new devices."""
        diff = DeepDiff(old_list, new_list)
        if diff:
            print("NetorgGenerator: Known devices (devices.yml) differences are as follows:")
            if 'iterable_item_added' in diff:
                print("  Adding devices:")
                added_dict = diff['iterable_item_added']
                # pylint: disable=unused-variable
                for key,val in added_dict.items():
                    print(f'    {val["group"]}: {val["name"]} {val["mac"]}')
            else:
                print("  There are no new devices")
        else:
            print("NetorgGenerator: There are no changes to known devices (devices.yml)")

    def generate(self) :
        """Genereate the known devices file (devices.yml)."""
        known_devices_generator = KnownDevicesGenerator()
        known_devices_loader = KnownDevicesLoader(self.devices_yml_path)
        before = known_devices_loader.load()
        print(f'Generating devices.yml file at {self.devices_yml_path}')
        with open(self.devices_yml_path, 'w', encoding='utf8') as devices_yml_file:
            devices_yml_file.write(known_devices_generator.generate(self.device_table))
        after = known_devices_loader.load()
        NetorgGenerator.show_diffs(before, after)

class KnownDevicesGenerator:
    """Generates the known devices file (devices.yml)."""

    # pylint: disable=invalid-name
    def get_devices_in_group(self, df, group, skip_these_macs) -> list :
        """Produce a list of all devices in a group."""
        devices = []
        # pylint: disable=unused-variable
        for index, row in df.query(f'group == "{group}"').iterrows():
            if row["mac"] not in skip_these_macs:
                devices.append(f'{row["name"]},{row["mac"]}')
            else:
                print(f'KnownDevicesGenerator: Skipping {row["name"]},{row["mac"]}')
        return devices

    def get_groups(self, df) -> list :
        """Produce a list of all unique groups in the device table."""
        return df.group.unique().tolist()

    def generate(self, device_table) -> str :
        """From the device table, generate the known devices file (devices.yml)."""
        yaml_lines = []
        yaml_lines.append("devices:")
        df = device_table.df
        skip_these_macs = df.query("not known and reserved and not active").mac.unique().tolist()
        groups = self.get_groups(df)
        for group_name in groups :
            if group_name == "" :
                # Classify unknown devices as unclassified
                yaml_lines.append("  unclassified:")
            else :
                yaml_lines.append(f'  {group_name}:')
            devices_in_group = self.get_devices_in_group(df,group_name,skip_these_macs)
            for device_in_group in devices_in_group :
                yaml_lines.append(f'    - {device_in_group}')
        s = '\n'.join(yaml_lines)
        return s
