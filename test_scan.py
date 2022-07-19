"""Tests for scan.py."""
import unittest
from devicetable import DeviceTableLoader
from scan import NetorgScanner

# pylint: disable=line-too-long
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
    """Test data for known devices."""

    known_devices_list = [
        {'name': 'k__', 'mac': 'k__', 'group': 'servers'},
        {'name': 'k_a', 'mac': 'k_a', 'group': 'printers'},
        {'name': 'kr_', 'mac': 'kr_', 'group': 'security'},
        {'name': 'kra', 'mac': 'kra', 'group': 'unclassified'}]

    @staticmethod
    def get_list_of_macs() :
        """Return list of MACs."""
        return [d['mac'] for d in MockKnownDevicesLoader.known_devices_list]

    # pylint: disable=unused-argument
    def load(self,filename='./devices.yml') -> list:
        """Load the test data."""
        return MockKnownDevicesLoader.known_devices_list

class MockActiveClientsLoader:
    """Test data for active clients."""

    active_clients_list = [
        {'mac': '__a', 'description': '__a',  'ip': '192.168.128.201'},
        {'mac': '_ra', 'description': '_ra',  'ip': '192.168.128.203'},
        {'mac': 'k_a', 'description': 'k_a',  'ip': '192.168.128.205'},
        {'mac': 'kra', 'description': 'kra',  'ip': '192.168.128.207'}]

    @staticmethod
    def get_list_of_macs() :
        """Return list of MACs."""
        return [d['mac'] for d in MockActiveClientsLoader.active_clients_list]

    def load(self) -> list:
        """Load the test data."""
        return MockActiveClientsLoader.active_clients_list

class MockFixedIpReservationsLoader:
    """Test data for fixed IP reservations."""

    reservations_dict = {
        '_r_': {'ip': '192.168.128.202', 'name': '_r_'},
        '_ra': {'ip': '192.168.128.203', 'name': '_ra'},
        'kr_': {'ip': '192.168.128.206', 'name': 'kr_'},
        'kra': {'ip': '192.168.128.207', 'name': 'kra'}}

    @staticmethod
    def get_list_of_macs() :
        """Return list of MACs."""
        return MockFixedIpReservationsLoader.reservations_dict.keys()

    def load(self) :
        """Load the test data."""
        return MockFixedIpReservationsLoader.reservations_dict

class TestNetorgScanner(unittest.TestCase) :
    """Tests for NetorgScanner."""

    def test_run(self):
        """Test NetorgScanner.run()."""
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
