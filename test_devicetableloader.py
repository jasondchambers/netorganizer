import unittest
from unittest.mock import patch, MagicMock
from devicetableloader import DeviceTableLoader, DeviceTableLoaderException


class MockClassifiedDevicesLoader:

    list = [
        {'name': 'Meerkat',         'mac': 'baa', 'group': 'servers'}, 
        {'name': 'Office Printer',  'mac': 'bab', 'group': 'printers'}, 
        {'name': 'Front Doorbell',  'mac': 'bba', 'group': 'security'},
        {'name': 'Driveway camera', 'mac': 'bbb', 'group': 'security'}]

    def load(self,filename='./devices.yml') -> list:
        return MockClassifiedDevicesLoader.list

class MockActiveClientsLoader:

    list = [
        {'mac': 'aab', 'description': 'HS105',  'ip': '192.168.128.201'}, 
        {'mac': 'abb', 'description': 'HS105',  'ip': '192.168.128.202'}, 
        {'mac': 'bab', 'description': 'Office Printer',  'ip': '192.168.128.203'}, 
        {'mac': 'bbb', 'description': 'Driveway camera',  'ip': '192.168.128.204'}]

    def load(self) -> list:
        return MockActiveClientsLoader.list

class MockFixedIpReservationsLoader:

    dict = { 
        'aba': {'ip': '192.168.128.191', 'name': 'Work Laptop'}, 
        'abb': {'ip': '192.168.128.202', 'name': 'HS105'}, 
        'bba': {'ip': '192.168.128.191', 'name': 'Echo 1'}, 
        'bbb': {'ip': '192.168.128.204', 'name': 'Echo 2'}}

    def load(self) :
        return MockFixedIpReservationsLoader.dict

class DeviceTableLoaderTest(unittest.TestCase) :
    """Test cases for DeviceTableLoader."""

    def test_load_classified(self) :
        mock_classified_devices_file_loader = MockClassifiedDevicesLoader()
        device_table_loader = DeviceTableLoader(mock_classified_devices_file_loader, None, None) 
        device_table_loader.load_classified()
        df = device_table_loader.device_table_builder.build().df
        classifed_df = df.loc[(df['classified'])] 
        active_df = df.loc[(df['active'])]
        fixed_ip_reservation_df = df.loc[(df['reserved'])]
        self.assertEqual(len(MockClassifiedDevicesLoader.list),classifed_df.shape[0])
        self.assertEqual(0,active_df.shape[0])
        self.assertEqual(0,fixed_ip_reservation_df.shape[0])

    def test_load_active(self) :
        mock_active_clients_loader = MockActiveClientsLoader()
        device_table_loader = DeviceTableLoader(None, mock_active_clients_loader, None) 
        device_table_loader.load_active_clients()
        df = device_table_loader.device_table_builder.build().df
        classifed_df = df.loc[(df['classified'])] 
        active_df = df.loc[(df['active'])]
        fixed_ip_reservation_df = df.loc[(df['reserved'])]
        self.assertEqual(0,classifed_df.shape[0])
        self.assertEqual(len(MockActiveClientsLoader.list),active_df.shape[0])
        self.assertEqual(0,fixed_ip_reservation_df.shape[0])

    def test_load_fixed_ip_reservations(self) :
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(None, None, mock_fixed_ip_reservations_loader) 
        device_table_loader.load_fixed_ip_reservations()
        df = device_table_loader.device_table_builder.build().df
        classifed_df = df.loc[(df['classified'])] 
        active_df = df.loc[(df['active'])]
        fixed_ip_reservation_df = df.loc[(df['reserved'])]
        self.assertEqual(0,classifed_df.shape[0])
        self.assertEqual(0,active_df.shape[0])
        self.assertEqual(len(MockFixedIpReservationsLoader.dict),fixed_ip_reservation_df.shape[0])

    def test_load_all(self) :
        mock_classified_devices_file_loader = MockClassifiedDevicesLoader()
        mock_active_clients_loader = MockActiveClientsLoader()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(mock_classified_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        df = device_table_loader.load_all()
        self.assertEqual(7,df.shape[0])
        classifed_df = df.loc[(df['classified'])] 
        active_df = df.loc[(df['active'])]
        fixed_ip_reservation_df = df.loc[(df['reserved'])]
        self.assertEqual(4,classifed_df.shape[0])
        self.assertEqual(4,active_df.shape[0])
        self.assertEqual(len(MockFixedIpReservationsLoader.dict),fixed_ip_reservation_df.shape[0])