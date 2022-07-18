import unittest
import pandas as pd
from generate import KnownDevicesGenerator, NetorgGenerator
from devicetable import DeviceTableBuilder
from knowndevicesloader import KnownDevicesLoader

class TestKnownDevicesGenerator(unittest.TestCase):
    
    def test_generate(self) : 
        device_table_builder = DeviceTableBuilder() 
        device_table_builder.set_details('18:90:88:28:eb:5b', { 
            'known': True, 
            'reserved': False, 
            'active': False, 
            'ip': '', 
            'group': 'eero', 
            'name': 'Eero Beacon Lady Pit'}) 
        device_table_builder.set_details('18:90:88:29:2b:5b', { 
            'known': True, 
            'reserved': False, 
            'active': False, 
            'ip': '', 
            'group': 'eero', 
            'name': 'Eero Beacon Family Room'})
        device_table_builder.set_details('68:a4:0e:2d:9a:91', { 
            'known': True, 
            'reserved': False, 
            'active': False, 
            'ip': '', 
            'group': 'kitchen_appliances', 
            'name': 'Kitchen Appliances Fridge'}) 
        device_table = device_table_builder.build() 
        known_devices_generator = KnownDevicesGenerator() 
        expected_yaml = "devices:\n"
        expected_yaml += "  eero:\n"
        expected_yaml += "    - Eero Beacon Lady Pit,18:90:88:28:eb:5b\n"
        expected_yaml += "    - Eero Beacon Family Room,18:90:88:29:2b:5b\n"
        expected_yaml += "  kitchen_appliances:\n"
        expected_yaml += "    - Kitchen Appliances Fridge,68:a4:0e:2d:9a:91\n"
        known_devices_loader = KnownDevicesLoader()
        expected = known_devices_loader.load_from_string(expected_yaml)
        df_expected = pd.DataFrame(expected)
        actual = known_devices_loader.load_from_string(known_devices_generator.generate(device_table))
        df_actual = pd.DataFrame(actual)
        self.assertEqual(True,df_actual.equals(df_expected))

    def test_show_diffs(self):
        old_yaml = "devices:\n"
        old_yaml += "  eero:\n"
        old_yaml += "    - Eero Beacon Lady Pit,18:90:88:28:eb:5b\n"
        old_yaml += "    - Eero Beacon Family Room,18:90:88:29:2b:5b\n"
        old_yaml += "  kitchen_appliances:\n"
        old_yaml += "    - Kitchen Appliances Fridge,68:a4:0e:2d:9a:91\n"
        known_devices_loader = KnownDevicesLoader()
        old_list = known_devices_loader.load_from_string(old_yaml)
        new_yaml = "devices:\n"
        new_yaml += "  eero:\n"
        new_yaml += "    - Eero Beacon Lady Pit,18:90:88:28:eb:5b\n"
        new_yaml += "    - Eero Beacon Family Room,18:90:88:29:2b:5b\n"
        new_yaml += "  kitchen_appliances:\n"
        new_yaml += "    - Kitchen Appliances Fridge,68:a4:0e:2d:9a:91\n"
        new_yaml += "  speakers:\n"
        new_yaml += "    - Den Speaker,68:a4:0e:2d:9a:95\n"
        known_devices_loader = KnownDevicesLoader()
        new_list = known_devices_loader.load_from_string(new_yaml)
        NetorgGenerator.show_diffs(old_list,new_list)
