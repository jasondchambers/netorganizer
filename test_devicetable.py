import unittest
#from unittest.mock import patch, MagicMock
from devicetable import DeviceTableBuilder, DeviceTableLoader, DeviceTableLoaderException

class TestDeviceTableBuilder(unittest.TestCase):
    def test_all(self) :
        device_table_builder = DeviceTableBuilder()
        device_table_builder.set_details('aab', {'known': False, 'reserved': False, 'active': True, 'ip': '192.168.128.10', 'group': '', 'name': 'JASCHAMB-M-XRDP'})
        device_table_builder.set_details('aba', {'known': False, 'reserved': True, 'active': False, 'ip': '192.168.128.50', 'group': '', 'name': 'LT6221'})
        device_table_builder.set_details('abb', {'known': False, 'reserved': True, 'active': True, 'ip': '192.168.128.51', 'group': '', 'name': 'HS105'})
        device_table_builder.set_details('baa', {'known': True, 'reserved': False, 'active': False, 'ip': '', 'group': 'printers', 'name': 'Aura-6141'})
        device_table_builder.set_details('bab', {'known': True, 'reserved': False, 'active': True, 'ip': '192.168.128.11', 'group': 'printers', 'name': 'Office'})
        device_table_builder.set_details('bba', {'known': True, 'reserved': True, 'active': False, 'ip': '192.168.128.100', 'group': 'laptops', 'name': 'Jason'})
        device_table_builder.set_details('bbb', {'known': True, 'reserved': True, 'active': True, 'ip': '192.168.128.101', 'group': 'laptops', 'name': 'Rose'})
        device_table = device_table_builder.build()

# Test table
#
TEST_TABLE_SIZE = 7
#   known | reserved (IP) | active | Description                | Action
# ==============+===============+========+======================+=======
#       0 |             0 |      0 |                            | 
# aab   0 |             0 |      1 | active                     | register the device
# aba   0 |             1 |      0 | reserved                   | remove reservation
# abb   0 |             1 |      1 | reserved & active          | register the device
# baa   1 |             0 |      0 | known                      | create reservation
# bab   1 |             0 |      1 | known & active             | convert to static reservation
# bba   1 |             1 |      0 | known & reserved           | 
# bbb   1 |             1 |      1 | known & reserved & active  | 

class MockKnownDevicesLoader:

    list = [
        {'name': 'Meerkat',         'mac': 'baa', 'group': 'servers'}, 
        {'name': 'Office Printer',  'mac': 'bab', 'group': 'printers'}, 
        {'name': 'Front Doorbell',  'mac': 'bba', 'group': 'security'},
        {'name': 'Driveway camera', 'mac': 'bbb', 'group': 'security'}]
    
    def get_list_of_macs() :
        return [d['mac'] for d in MockKnownDevicesLoader.list]

    def load(self,filename='./devices.yml') -> list:
        return MockKnownDevicesLoader.list

class MockActiveClientsLoader:

    list = [
        {'mac': 'aab', 'description': 'HS105',  'ip': '192.168.128.201'}, 
        {'mac': 'abb', 'description': 'HS105',  'ip': '192.168.128.202'}, 
        {'mac': 'bab', 'description': 'Office Printer',  'ip': '192.168.128.203'}, 
        {'mac': 'bbb', 'description': 'Driveway camera',  'ip': '192.168.128.204'}]

    def get_list_of_macs() :
        return [d['mac'] for d in MockActiveClientsLoader.list]

    def load(self) -> list:
        return MockActiveClientsLoader.list

class MockFixedIpReservationsLoader:

    dict = { 
        'aba': {'ip': '192.168.128.191', 'name': 'Work Laptop'}, 
        'abb': {'ip': '192.168.128.202', 'name': 'HS105'}, 
        'bba': {'ip': '192.168.128.191', 'name': 'Echo 1'}, 
        'bbb': {'ip': '192.168.128.204', 'name': 'Echo 2'}}

    def get_list_of_macs() :
        return MockFixedIpReservationsLoader.dict.keys()

    def load(self) :
        return MockFixedIpReservationsLoader.dict

class MockDuplicateMacKnownDevicesLoader:

    list = [
        # Duplicate MAC addresses
        {'name': 'Meerkat',         'mac': 'aaa', 'group': 'servers'}, 
        {'name': 'Office Printer',  'mac': 'aaa', 'group': 'printers'}]
    
    def get_list_of_macs() :
        return [d['mac'] for d in MockDuplicateMacKnownDevicesLoader.list]

    def load(self,filename='./devices.yml') -> list:
        return MockDuplicateMacKnownDevicesLoader.list

class TestDeviceTableLoader(unittest.TestCase) :
    """Test cases for DeviceTableLoader."""

    def test_load_known(self) :
        mock_known_devices_file_loader = MockKnownDevicesLoader()
        device_table_loader = DeviceTableLoader(mock_known_devices_file_loader, None, None) 
        device_table_loader.load_known()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(len(MockKnownDevicesLoader.list),df.query("known").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_active(self) :
        mock_active_clients_loader = MockActiveClientsLoader()
        device_table_loader = DeviceTableLoader(None, mock_active_clients_loader, None) 
        device_table_loader.load_active_clients()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(0,df.query("known").shape[0])
        self.assertEqual(len(MockActiveClientsLoader.list),df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_fixed_ip_reservations(self) :
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(None, None, mock_fixed_ip_reservations_loader) 
        device_table_loader.load_fixed_ip_reservations()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(0,df.query("known").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(len(MockFixedIpReservationsLoader.dict),df.query("reserved").shape[0])

    def test_load_all(self) :
        mock_known_devices_file_loader = MockKnownDevicesLoader()
        mock_active_clients_loader = MockActiveClientsLoader()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(mock_known_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        df = device_table_loader.load_all().df
        self.assertEqual(TEST_TABLE_SIZE,df.shape[0])

        # known
        self.assertEqual(len(MockKnownDevicesLoader.get_list_of_macs()),df.query("known").shape[0])
        for mac in MockKnownDevicesLoader.get_list_of_macs() : 
            self.assertIn(mac,df.query("known")["mac"].tolist())

        # active
        self.assertEqual(len(MockActiveClientsLoader.get_list_of_macs()),df.query("active").shape[0])
        for mac in MockActiveClientsLoader.get_list_of_macs() :
            self.assertIn(mac,df.query("active")["mac"].tolist())

        # reserved
        self.assertEqual(len(MockFixedIpReservationsLoader.get_list_of_macs()),df.query("reserved").shape[0])
        for mac in MockFixedIpReservationsLoader.get_list_of_macs() :
            self.assertIn(mac,df.query("reserved")["mac"].tolist())
        
        # known and active
        known_set = set(MockKnownDevicesLoader.get_list_of_macs())
        active_set = set(MockActiveClientsLoader.get_list_of_macs())
        expected = known_set.intersection(active_set)
        actual = df.query("known and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # known and reserved
        reserved_set = set(MockFixedIpReservationsLoader.get_list_of_macs())
        expected = known_set.intersection(reserved_set)
        actual = df.query("known and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # active and reserved
        expected = active_set.intersection(reserved_set)
        actual = df.query("active and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # known and reserved and active
        expected = known_set.intersection(reserved_set,active_set)
        actual = df.query("known and reserved and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))