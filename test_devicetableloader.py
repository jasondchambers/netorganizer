import unittest
from unittest.mock import patch, MagicMock
from devicetableloader import DeviceTableLoader, DeviceTableLoaderException

# Test table
#
TEST_TABLE_SIZE = 7
#    registered | reserved (IP) | active | Description                     | Action
# ==============+===============+========+=================================+=======
#             0 |             0 |      0 |                                 | N/A
# aab         0 |             0 |      1 | active                          | Ask user to classify 
# aba         0 |             1 |      0 | reserved                        | Remove reservation
# abb         0 |             1 |      1 | reserved & active               | Ask user to classify
# baa         1 |             0 |      0 | registered                      | Create reservation
# bab         1 |             0 |      1 | registered & active             | Convert to static reservation
# bba         1 |             1 |      0 | registered & reserved           | No change
# bbb         1 |             1 |      1 | registered & reserved & active  | No change

class MockRegisteredDevicesLoader:

    list = [
        {'name': 'Meerkat',         'mac': 'baa', 'group': 'servers'}, 
        {'name': 'Office Printer',  'mac': 'bab', 'group': 'printers'}, 
        {'name': 'Front Doorbell',  'mac': 'bba', 'group': 'security'},
        {'name': 'Driveway camera', 'mac': 'bbb', 'group': 'security'}]
    
    def get_list_of_macs() :
        return [d['mac'] for d in MockRegisteredDevicesLoader.list]

    def load(self,filename='./devices.yml') -> list:
        return MockRegisteredDevicesLoader.list

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

class MockDuplicateMacRegisteredDevicesLoader:

    list = [
        # Duplicate MAC addresses
        {'name': 'Meerkat',         'mac': 'aaa', 'group': 'servers'}, 
        {'name': 'Office Printer',  'mac': 'aaa', 'group': 'printers'}]
    
    def get_list_of_macs() :
        return [d['mac'] for d in MockDuplicateMacRegisteredDevicesLoader.list]

    def load(self,filename='./devices.yml') -> list:
        return MockDuplicateMacRegisteredDevicesLoader.list

class DeviceTableLoaderTest(unittest.TestCase) :
    """Test cases for DeviceTableLoader."""

    def test_load_registered(self) :
        mock_registered_devices_file_loader = MockRegisteredDevicesLoader()
        device_table_loader = DeviceTableLoader(mock_registered_devices_file_loader, None, None) 
        device_table_loader.load_registered()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(len(MockRegisteredDevicesLoader.list),df.query("registered").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_active(self) :
        mock_active_clients_loader = MockActiveClientsLoader()
        device_table_loader = DeviceTableLoader(None, mock_active_clients_loader, None) 
        device_table_loader.load_active_clients()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(0,df.query("registered").shape[0])
        self.assertEqual(len(MockActiveClientsLoader.list),df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_fixed_ip_reservations(self) :
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(None, None, mock_fixed_ip_reservations_loader) 
        device_table_loader.load_fixed_ip_reservations()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(0,df.query("registered").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(len(MockFixedIpReservationsLoader.dict),df.query("reserved").shape[0])

    def test_load_all(self) :
        mock_registered_devices_file_loader = MockRegisteredDevicesLoader()
        mock_active_clients_loader = MockActiveClientsLoader()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(mock_registered_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        df = device_table_loader.load_all().df
        self.assertEqual(TEST_TABLE_SIZE,df.shape[0])

        # registered
        self.assertEqual(len(MockRegisteredDevicesLoader.get_list_of_macs()),df.query("registered").shape[0])
        for mac in MockRegisteredDevicesLoader.get_list_of_macs() : 
            self.assertIn(mac,df.query("registered")["mac"].tolist())

        # active
        self.assertEqual(len(MockActiveClientsLoader.get_list_of_macs()),df.query("active").shape[0])
        for mac in MockActiveClientsLoader.get_list_of_macs() :
            self.assertIn(mac,df.query("active")["mac"].tolist())

        # reserved
        self.assertEqual(len(MockFixedIpReservationsLoader.get_list_of_macs()),df.query("reserved").shape[0])
        for mac in MockFixedIpReservationsLoader.get_list_of_macs() :
            self.assertIn(mac,df.query("reserved")["mac"].tolist())
        
        # registered and active
        registered_set = set(MockRegisteredDevicesLoader.get_list_of_macs())
        active_set = set(MockActiveClientsLoader.get_list_of_macs())
        expected = registered_set.intersection(active_set)
        actual = df.query("registered and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # registered and reserved
        reserved_set = set(MockFixedIpReservationsLoader.get_list_of_macs())
        expected = registered_set.intersection(reserved_set)
        actual = df.query("registered and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # active and reserved
        expected = active_set.intersection(reserved_set)
        actual = df.query("active and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # registered and reserved and active
        expected = registered_set.intersection(reserved_set,active_set)
        actual = df.query("registered and reserved and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

    def test_load_duplicate_mac_registered(self) :
        mock_duplicate_mac_registered_devices_file_loader = MockDuplicateMacRegisteredDevicesLoader()
        device_table_loader = DeviceTableLoader(mock_duplicate_mac_registered_devices_file_loader, None, None) 
        device_table_loader.load_registered()
        device_table = device_table_loader.device_table_builder.build()
        # Although the loaded data has duplicate MACs, the way it is loaded - the last
        # device wins and there will only be one MAC - hence it will be valid
        self.assertTrue(device_table.is_valid())
