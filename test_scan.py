import unittest
from devicetable import DeviceTableLoader
from scan import NetorgScanner

# Test table
#
#   known | reserved (IP) | active | Description                                | Action
# ========+===============+========+============================================+=======
#       0 |             0 |      0 |                                            | 
# __a   0 |             0 |      1 | active                                     | register the device
# _r_   0 |             1 |      0 | reserved                                   | remove reservation
# _ra   0 |             1 |      1 | reserved & active                          | register the device
# k__   1 |             0 |      0 | known                                      | create reservation
# k_a   1 |             0 |      1 | known & active                             | convert to static reservation
# kr_   1 |             1 |      0 | known & reserved                           | 
# kra   1 |             1 |      1 | known & reserved & active (& unclassified) | invite classification

class MockKnownDevicesLoader:

    list = [
        {'name': 'k__', 'mac': 'k__', 'group': 'servers'}, 
        {'name': 'k_a', 'mac': 'k_a', 'group': 'printers'}, 
        {'name': 'kr_', 'mac': 'kr_', 'group': 'security'},
        {'name': 'kra', 'mac': 'kra', 'group': 'unclassified'}]
    
    def get_list_of_macs() :
        return [d['mac'] for d in MockKnownDevicesLoader.list]

    def load(self,filename='./devices.yml') -> list:
        return MockKnownDevicesLoader.list

class MockActiveClientsLoader:

    list = [
        {'mac': '__a', 'description': '__a',  'ip': '192.168.128.201'}, 
        {'mac': '_ra', 'description': '_ra',  'ip': '192.168.128.202'}, 
        {'mac': 'k_a', 'description': 'k_a',  'ip': '192.168.128.203'}, 
        {'mac': 'kra', 'description': 'kra',  'ip': '192.168.128.204'}]

    def get_list_of_macs() :
        return [d['mac'] for d in MockActiveClientsLoader.list]

    def load(self) -> list:
        return MockActiveClientsLoader.list

class MockFixedIpReservationsLoader:

    dict = { 
        '_r_': {'ip': '192.168.128.191', 'name': '_r_'}, 
        '_ra': {'ip': '192.168.128.202', 'name': '_ra'}, 
        'kr_': {'ip': '192.168.128.191', 'name': 'kr_'}, 
        'kra': {'ip': '192.168.128.204', 'name': 'kra'}}

    def get_list_of_macs() :
        return MockFixedIpReservationsLoader.dict.keys()

    def load(self) :
        return MockFixedIpReservationsLoader.dict

class TestNetorgScanner(unittest.TestCase) :

    def test_run(self):
        mock_known_devices_file_loader = MockKnownDevicesLoader()
        mock_active_clients_loader = MockActiveClientsLoader()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(mock_known_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        device_table = device_table_loader.load_all()
        scanner = NetorgScanner(device_table)
        scanner.run()
        analysis = scanner.analysis
        self.assertListEqual(analysis['not_known_not_reserved_ACTIVE']['device_names'], ['__a'])
        self.assertListEqual(analysis['not_known_RESERVED_not_active']['device_names'], ['_r_'])
        self.assertListEqual(analysis['not_known_RESERVED_ACTIVE']['device_names'], ['_ra'])
        self.assertListEqual(analysis['KNOWN_not_reserved_not_active']['device_names'], ['k__'])
        self.assertListEqual(analysis['KNOWN_RESERVED_not_active']['device_names'], ['kr_'])
        self.assertListEqual(analysis['KNOWN_RESERVED_ACTIVE']['device_names'], ['kra'])
        actual = analysis['ACTIVE_UNCLASSIFIED']['device_names']
        actual.sort()
        expected = ['__a', '_ra', 'kra']
        expected.sort()
        self.assertListEqual(actual, expected)


