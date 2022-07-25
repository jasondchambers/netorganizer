"""Tests for generate.py."""
import unittest
import pandas as pd
from generate import KnownDevicesGenerator, NetorgGenerator
from devicetable import DeviceTableBuilder, DeviceTableLoader
from knowndevicesloader import KnownDevicesLoader
from netorgmeraki import MerakiFixedIpReservationsGenerator

class MockKnownDevicesLoader:
    """Test data for known devices."""

    known_devices_list = [
        {'name': 'k__', 'mac': 'k__', 'group': 'servers'},
        {'name': 'k_a', 'mac': 'k_a', 'group': 'printers'},
        {'name': 'kr_', 'mac': 'kr_', 'group': 'security'},
        {'name': 'kra', 'mac': 'kra', 'group': 'unclassified'}
    ]

    @staticmethod
    def get_list_of_macs() :
        """Return list of MACs."""
        return [d['mac'] for d in MockKnownDevicesLoader.known_devices_list]

    # pylint: disable=unused-argument
    def load(self, filename='./devices.yml') -> list:
        """Load the test data."""
        return MockKnownDevicesLoader.known_devices_list

class MockActiveClientsLoader:
    """Test data for active clients."""

    active_clients_list = [
        {'mac': '__a', 'description': '__a',  'ip': '192.168.128.201'},
        {'mac': '_ra', 'description': '_ra',  'ip': '192.168.128.203'},
        {'mac': 'k_a', 'description': 'k_a',  'ip': '192.168.128.205'},
        {'mac': 'kra', 'description': 'kra',  'ip': '192.168.128.207'}
    ]

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
        'kra': {'ip': '192.168.128.207', 'name': 'kra'}
    }

    @staticmethod
    def get_list_of_macs() :
        """Return list of MACs."""
        return MockFixedIpReservationsLoader.reservations_dict.keys()

    def load(self) :
        """Load the test data."""
        return MockFixedIpReservationsLoader.reservations_dict

class TestKnownDevicesGenerator(unittest.TestCase):
    """Tests for KnownDevicesGenerator."""

    def test_generate(self) :
        """Test KnownDevicesGenerator.generate()."""
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
        expected = list(known_devices_loader.load_from_string(expected_yaml))
        df_expected = pd.DataFrame(expected)
        actual = list(known_devices_loader.load_from_string(
            known_devices_generator.generate(device_table)))
        df_actual = pd.DataFrame(actual)
        self.assertEqual(True,df_actual.equals(df_expected))

    def test_show_diffs(self):
        """Test NetorgGenerator.show_diffs."""
        old_yaml = "devices:\n"
        old_yaml += "  eero:\n"
        old_yaml += "    - Eero Beacon Lady Pit,18:90:88:28:eb:5b\n"
        old_yaml += "    - Eero Beacon Family Room,18:90:88:29:2b:5b\n"
        old_yaml += "  kitchen_appliances:\n"
        old_yaml += "    - Kitchen Appliances Fridge,68:a4:0e:2d:9a:91\n"
        known_devices_loader = KnownDevicesLoader()
        old_list = list(known_devices_loader.load_from_string(old_yaml))
        new_yaml = "devices:\n"
        new_yaml += "  eero:\n"
        new_yaml += "    - Eero Beacon Lady Pit,18:90:88:28:eb:5b\n"
        new_yaml += "    - Eero Beacon Family Room,18:90:88:29:2b:5b\n"
        new_yaml += "  kitchen_appliances:\n"
        new_yaml += "    - Kitchen Appliances Fridge,68:a4:0e:2d:9a:91\n"
        new_yaml += "  speakers:\n"
        new_yaml += "    - Den Speaker,68:a4:0e:2d:9a:95\n"
        known_devices_loader = KnownDevicesLoader()
        new_list = list(known_devices_loader.load_from_string(new_yaml))
        NetorgGenerator.show_diffs(old_list,new_list)

    def test_meraki_fixed_ip_reservations_generator(self):
        """ Test MerakiFixedIpReservationsGenerator.generate()."""
        device_table_loader = DeviceTableLoader(MockKnownDevicesLoader(),
                                                MockActiveClientsLoader(),
                                                MockFixedIpReservationsLoader())
        device_table = device_table_loader.load_all()
        MerakiFixedIpReservationsGenerator.generate(device_table)
