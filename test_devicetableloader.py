import unittest
from unittest.mock import patch, MagicMock
from devicetableloader import DeviceTableLoader, DeviceTableLoaderException

# Test table
#
TEST_TABLE_SIZE = 7
#    classified | reserved (IP) | active | Description                     | Action
# ==============+===============+========+=================================+=======
#             0 |             0 |      0 |                                 | N/A
# aab         0 |             0 |      1 | active                          | Ask user to classify 
# aba         0 |             1 |      0 | reserved                        | Remove reservation
# abb         0 |             1 |      1 | reserved & active               | Ask user to classify
# baa         1 |             0 |      0 | classified                      | Create reservation
# bab         1 |             0 |      1 | classified & active             | Convert to static reservation
# bba         1 |             1 |      0 | classified & reserved           | No change
# bbb         1 |             1 |      1 | classified & reserved & active  | No change

class MockClassifiedDevicesLoader:

    list = [
        {'name': 'Meerkat',         'mac': 'baa', 'group': 'servers'}, 
        {'name': 'Office Printer',  'mac': 'bab', 'group': 'printers'}, 
        {'name': 'Front Doorbell',  'mac': 'bba', 'group': 'security'},
        {'name': 'Driveway camera', 'mac': 'bbb', 'group': 'security'}]
    
    def get_list_of_macs() :
        return [d['mac'] for d in MockClassifiedDevicesLoader.list]

    def load(self,filename='./devices.yml') -> list:
        return MockClassifiedDevicesLoader.list

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

class DeviceTableLoaderTest(unittest.TestCase) :
    """Test cases for DeviceTableLoader."""

    def test_load_classified(self) :
        mock_classified_devices_file_loader = MockClassifiedDevicesLoader()
        device_table_loader = DeviceTableLoader(mock_classified_devices_file_loader, None, None) 
        device_table_loader.load_classified()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(len(MockClassifiedDevicesLoader.list),df.query("classified").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_active(self) :
        mock_active_clients_loader = MockActiveClientsLoader()
        device_table_loader = DeviceTableLoader(None, mock_active_clients_loader, None) 
        device_table_loader.load_active_clients()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(0,df.query("classified").shape[0])
        self.assertEqual(len(MockActiveClientsLoader.list),df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_fixed_ip_reservations(self) :
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(None, None, mock_fixed_ip_reservations_loader) 
        device_table_loader.load_fixed_ip_reservations()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(0,df.query("classified").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(len(MockFixedIpReservationsLoader.dict),df.query("reserved").shape[0])

    def test_load_all(self) :
        mock_classified_devices_file_loader = MockClassifiedDevicesLoader()
        mock_active_clients_loader = MockActiveClientsLoader()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(mock_classified_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        df = device_table_loader.load_all()
        self.assertEqual(TEST_TABLE_SIZE,df.shape[0])

        # classified
        self.assertEqual(len(MockClassifiedDevicesLoader.get_list_of_macs()),df.query("classified").shape[0])
        for mac in MockClassifiedDevicesLoader.get_list_of_macs() : 
            self.assertIn(mac,df.query("classified")["mac"].tolist())

        # active
        self.assertEqual(len(MockActiveClientsLoader.get_list_of_macs()),df.query("active").shape[0])
        for mac in MockActiveClientsLoader.get_list_of_macs() :
            self.assertIn(mac,df.query("active")["mac"].tolist())

        # reserved
        self.assertEqual(len(MockFixedIpReservationsLoader.get_list_of_macs()),df.query("reserved").shape[0])
        for mac in MockFixedIpReservationsLoader.get_list_of_macs() :
            self.assertIn(mac,df.query("reserved")["mac"].tolist())
        
        # classified and active
        classified_set = set(MockClassifiedDevicesLoader.get_list_of_macs())
        active_set = set(MockActiveClientsLoader.get_list_of_macs())
        expected = classified_set.intersection(active_set)
        actual = df.query("classified and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # classified and reserved
        reserved_set = set(MockFixedIpReservationsLoader.get_list_of_macs())
        expected = classified_set.intersection(reserved_set)
        actual = df.query("classified and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # active and reserved
        expected = active_set.intersection(reserved_set)
        actual = df.query("active and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # classified and reserved and active
        expected = classified_set.intersection(reserved_set,active_set)
        actual = df.query("classified and reserved and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))