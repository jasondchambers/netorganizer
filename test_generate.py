import unittest
import pandas as pd
from generate import RegisteredDevicesGenerator
from devicetable import DeviceTableBuilder
from registereddevicesloader import RegisteredDevicesLoader

class TestRegisteredDevicesGenerator(unittest.TestCase):
    
    def test_generate(self) : 
        device_table_builder = DeviceTableBuilder() 
        device_table_builder.set_details('18:90:88:28:eb:5b', { 
            'registered': True, 
            'reserved': False, 
            'active': False, 
            'ip': '', 
            'group': 'eero', 
            'name': 'Eero Beacon Lady Pit'}) 
        device_table_builder.set_details('18:90:88:29:2b:5b', { 
            'registered': True, 
            'reserved': False, 
            'active': False, 
            'ip': '', 
            'group': 'eero', 
            'name': 'Eero Beacon Family Room'})
        device_table_builder.set_details('68:a4:0e:2d:9a:91', { 
            'registered': True, 
            'reserved': False, 
            'active': False, 
            'ip': '', 
            'group': 'kitchen_appliances', 
            'name': 'Kitchen Appliances Fridge'}) 
        device_table = device_table_builder.build() 
        registered_devices_generator = RegisteredDevicesGenerator() 
        expected_yaml = "devices:\n"
        expected_yaml += "  eero:\n"
        expected_yaml += "    - Eero Beacon Lady Pit,18:90:88:28:eb:5b\n"
        expected_yaml += "    - Eero Beacon Family Room,18:90:88:29:2b:5b\n"
        expected_yaml += "  kitchen_appliances:\n"
        expected_yaml += "    - Kitchen Appliances Fridge,68:a4:0e:2d:9a:91\n"
        registered_devices_loader = RegisteredDevicesLoader()
        expected = registered_devices_loader.load_from_string(expected_yaml)
        df_expected = pd.DataFrame(expected)
        actual = registered_devices_loader.load_from_string(registered_devices_generator.generate(device_table))
        df_actual = pd.DataFrame(actual)
        self.assertEqual(True,df_actual.equals(df_expected))