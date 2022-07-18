import unittest
import pandas as pd
from generate import KnownDevicesGenerator, NetorgGenerator
from devicetable import DeviceTableBuilder, DeviceTableLoader
from knowndevicesloader import KnownDevicesLoader
from netorgmeraki import MerakiFixedIpReservationsGenerator

class MockKnownDevicesLoader:
    list = [
        {'name': 'k__', 'mac': 'k__', 'group': 'servers'}, 
        {'name': 'k_a', 'mac': 'k_a', 'group': 'printers'}, 
        {'name': 'kr_', 'mac': 'kr_', 'group': 'security'},
        {'name': 'kra', 'mac': 'kra', 'group': 'unclassified'}
    ]
    def get_list_of_macs() :
        return [d['mac'] for d in MockKnownDevicesLoader.list]
    def load(self,filename='./devices.yml') -> list:
        return MockKnownDevicesLoader.list

class MockActiveClientsLoader:
    list = [
        {'mac': '__a', 'description': '__a',  'ip': '192.168.128.201'}, 
        {'mac': '_ra', 'description': '_ra',  'ip': '192.168.128.203'}, 
        {'mac': 'k_a', 'description': 'k_a',  'ip': '192.168.128.205'}, 
        {'mac': 'kra', 'description': 'kra',  'ip': '192.168.128.207'}
    ]
    def get_list_of_macs() :
        return [d['mac'] for d in MockActiveClientsLoader.list]
    def load(self) -> list:
        return MockActiveClientsLoader.list

class MockFixedIpReservationsLoader:
    dict = { 
        '_r_': {'ip': '192.168.128.202', 'name': '_r_'}, 
        '_ra': {'ip': '192.168.128.203', 'name': '_ra'}, 
        'kr_': {'ip': '192.168.128.206', 'name': 'kr_'}, 
        'kra': {'ip': '192.168.128.207', 'name': 'kra'}
    }
    def get_list_of_macs() :
        return MockFixedIpReservationsLoader.dict.keys()
    def load(self) :
        return MockFixedIpReservationsLoader.dict

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

    def test_meraki_fixed_ip_reservations_generator(self):
        mock_known_devices_file_loader = MockKnownDevicesLoader()
        mock_active_clients_loader = MockActiveClientsLoader()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(mock_known_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        device_table = device_table_loader.load_all()
        MerakiFixedIpReservationsGenerator.generate(device_table)
