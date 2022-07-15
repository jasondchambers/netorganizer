import unittest

from devicetable import DeviceTableLoader
from ipv4privatenetworkspace import NetworkIsOutOfSpace
from netorgmeraki import MerakiNetworkMapper

# Test table
#
#   known | reserved (IP) | IP   | active | Description                                | Action
# ========+===============+======+========+===========================================+=======
#       0 |             0 |      |      0 |                                            | 
# __a   0 |             0 | .201 |      1 | active                                     | register the device
# _r_   0 |             1 | .202 |      0 | reserved                                   | remove reservation
# _ra   0 |             1 | .203 |      1 | reserved & active                          | register the device
# k__   1 |             0 |      |      0 | known                                      | create reservation
# k_a   1 |             0 | .205 |      1 | known & active                             | convert to static reservation
# kr_   1 |             1 | .206 |      0 | known & reserved                           | 
# kra   1 |             1 | .207 |      1 | known & reserved & active (& unclassified) | invite classification

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

class MockKnownDevicesLoaderForOutOfSpaceTest:
    list = [{'name': 'k__', 'mac': 'k__', 'group': 'servers'}]
    def get_list_of_macs() :
        return [d['mac'] for d in MockKnownDevicesLoaderForOutOfSpaceTest.list]
    def load(self,filename='./devices.yml') -> list:
        return MockKnownDevicesLoaderForOutOfSpaceTest.list

class MockActiveClientsLoaderForOutOfSpaceTest:
    list = [{'mac': '_ra', 'description': '_ra',  'ip': '192.168.128.254'}]
    def get_list_of_macs() :
        return [d['mac'] for d in MockActiveClientsLoaderForOutOfSpaceTest.list]
    def load(self) -> list:
        return MockActiveClientsLoaderForOutOfSpaceTest.list

class MockFixedIpReservationsLoaderForOutOfSpaceTest:
    dict = {'_r_': {'ip': '192.168.128.253', 'name': '_r_'}}
    def get_list_of_macs() :
        return MockFixedIpReservationsLoaderForOutOfSpaceTest.dict.keys()
    def load(self) :
        return MockFixedIpReservationsLoaderForOutOfSpaceTest.dict

class MockKnownDevicesLoaderForDuplicateIpTest:
    list = [
        {'name': 'k__', 'mac': 'k__', 'group': 'servers'}, 
        {'name': 'k_a', 'mac': 'k_a', 'group': 'printers'}, 
        {'name': 'kr_', 'mac': 'kr_', 'group': 'security'},
        {'name': 'kra', 'mac': 'kra', 'group': 'unclassified'}
    ]
    def get_list_of_macs() :
        return [d['mac'] for d in MockKnownDevicesLoaderForDuplicateIpTest.list]
    def load(self,filename='./devices.yml') -> list:
        return MockKnownDevicesLoaderForDuplicateIpTest.list

class MockActiveClientsLoaderForDuplicateIpTest:
    list = [
        {'mac': '__a', 'description': '__a',  'ip': '192.168.128.201'}, 
        {'mac': '_ra', 'description': '_ra',  'ip': '192.168.128.203'}, 
        {'mac': 'k_a', 'description': 'k_a',  'ip': '192.168.128.205'}, 
        {'mac': 'kra', 'description': 'kra',  'ip': '192.168.128.202'} # Duplicate IP with _r_
    ]
    def get_list_of_macs() :
        return [d['mac'] for d in MockActiveClientsLoaderForDuplicateIpTest.list]
    def load(self) -> list:
        return MockActiveClientsLoaderForDuplicateIpTest.list

class MockFixedIpReservationsLoaderForDuplicateIpTest:
    dict = { 
        '_r_': {'ip': '192.168.128.202', 'name': '_r_'}, 
        '_ra': {'ip': '192.168.128.203', 'name': '_ra'}, 
        'kr_': {'ip': '192.168.128.206', 'name': 'kr_'}, 
        'kra': {'ip': '192.168.128.202', 'name': 'kra'} # Duplicate IP with _r_
    }
    def get_list_of_macs() :
        return MockFixedIpReservationsLoaderForDuplicateIpTest.dict.keys()
    def load(self) :
        return MockFixedIpReservationsLoaderForDuplicateIpTest.dict

class MockKnownDevicesLoaderForIpReservationGeneratorTest:
    def get_list_of_macs() :
        return []
    def load(self,filename='./devices.yml') -> list:
        return []

class MockActiveClientsLoaderForIpReservationGeneratorTest:
    list = [
        {'mac': '__a_201', 'description': '__a_201',  'ip': '192.168.128.201'}, 
        {'mac': '__a_202', 'description': '__a_202',  'ip': '192.168.128.202'}
    ]
    def get_list_of_macs() :
        return [d['mac'] for d in MockActiveClientsLoaderForIpReservationGeneratorTest.list]
    def load(self) -> list:
        return MockActiveClientsLoaderForIpReservationGeneratorTest.list

class MockFixedIpReservationsLoaderForIpReservationGeneratorTest:
    dict = { 
        '_r__203': {'ip': '192.168.128.203', 'name': '_r__203'}, # Expect this to be skipped because it is not known and not active 
    }
    def get_list_of_macs() :
        return MockFixedIpReservationsLoaderForIpReservationGeneratorTest.dict.keys()
    def load(self) :
        return MockFixedIpReservationsLoaderForIpReservationGeneratorTest.dict

class TestNetorgOrganizer(unittest.TestCase) :

    def test_organize(self):
        mock_known_devices_file_loader = MockKnownDevicesLoader()
        mock_active_clients_loader = MockActiveClientsLoader()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(mock_known_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        device_table = device_table_loader.load_all()
        config = {
            "vlan_subnet": "192.168.128.0/24"
        }
        devices_with_no_ip = device_table.df.query("ip == ''")['mac'].tolist() 
        self.assertEqual(1, len(devices_with_no_ip), "Expected there to be one device needing an IP")
        meraki_network_mapper = MerakiNetworkMapper(config, device_table)
        devices_with_no_ip = device_table.df.query("ip == ''")['mac'].tolist() 
        self.assertEqual(0, len(devices_with_no_ip), "Expected there to be zero devices needing an IP")

    def test_invalid_subnet(self):
        mock_known_devices_file_loader = MockKnownDevicesLoader()
        mock_active_clients_loader = MockActiveClientsLoader()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoader()
        device_table_loader = DeviceTableLoader(mock_known_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        device_table = device_table_loader.load_all()
        config = {
            "vlan_subnet": "192.168.128.252/30" # Different subnet to the IPs in the test data
        }
        self.assertRaises(ValueError, MerakiNetworkMapper, config, device_table)

    def test_not_enough_network_space(self) :
        mock_known_devices_file_loader = MockKnownDevicesLoaderForOutOfSpaceTest()
        mock_active_clients_loader = MockActiveClientsLoaderForOutOfSpaceTest()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoaderForOutOfSpaceTest()
        device_table_loader = DeviceTableLoader(mock_known_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        device_table = device_table_loader.load_all()
        config = {
            "vlan_subnet": "192.168.128.252/30" 
        }
        devices_with_no_ip = device_table.df.query("ip == ''")['mac'].tolist() 
        self.assertEqual(1, len(devices_with_no_ip), "Expected there to be one device needing an IP")
        self.assertRaises(NetworkIsOutOfSpace, MerakiNetworkMapper, config, device_table)

    def test_duplicate_ips_in_device_table(self) :
        mock_known_devices_file_loader = MockKnownDevicesLoaderForDuplicateIpTest()
        mock_active_clients_loader = MockActiveClientsLoaderForDuplicateIpTest()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoaderForDuplicateIpTest()
        device_table_loader = DeviceTableLoader(mock_known_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        device_table = device_table_loader.load_all()
        config = {
            "vlan_subnet": "192.168.128.0/24"
        }
        self.assertRaises(ValueError, MerakiNetworkMapper, config, device_table)

    def test_generate_ip_reservations(self):
        mock_known_devices_file_loader = MockKnownDevicesLoaderForIpReservationGeneratorTest()
        mock_active_clients_loader = MockActiveClientsLoaderForIpReservationGeneratorTest()
        mock_fixed_ip_reservations_loader = MockFixedIpReservationsLoaderForIpReservationGeneratorTest()
        device_table_loader = DeviceTableLoader(mock_known_devices_file_loader, mock_active_clients_loader, mock_fixed_ip_reservations_loader) 
        device_table = device_table_loader.load_all()
        config = {
            "vlan_subnet": "192.168.128.0/24"
        }
        print(device_table.df)
        meraki_network_mapper = MerakiNetworkMapper(config, device_table)
        fixed_ip_reservations = meraki_network_mapper.generate_fixed_ip_reservations()
        self.assertEqual(len(fixed_ip_reservations), 2, "Expected there to be 2 reservations")
        self.assertEqual(fixed_ip_reservations['__a_201']['ip'], '192.168.128.201')
        self.assertEqual(fixed_ip_reservations['__a_202']['ip'], '192.168.128.202')
        print(fixed_ip_reservations)