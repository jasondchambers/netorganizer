"""Module for testing knowndevicesloader."""

import unittest
import tempfile
from knowndevicesloader import KnownDevicesLoader

class TestKnownDevicesLoader(unittest.TestCase):
    """Tests for KnownDevicesLoader."""

    @staticmethod
    def generate_test_data() -> str:
        """Generate well-formed YAML for testing."""
        good_yaml = "devices:\n"
        good_yaml += "  eero:\n"
        good_yaml += "    - Eero Beacon Lady Pit,18:90:88:28:eb:5b\n"
        good_yaml += "    - Eero Beacon Family Room,18:90:88:29:2b:5b\n"
        good_yaml += "  kitchen_appliances:\n"
        good_yaml += "    - Kitchen Appliances Fridge,68:a4:0e:2d:9a:91\n"
        return good_yaml

    def inspect_output(self, devices):
        """Inspect the out output from test."""
        self.assertEqual(3, len(devices))
        for device in devices:
            if device['name'] == 'Eero Beacon Lady Pit':
                self.assertEqual(device['mac'], '18:90:88:28:eb:5b')
                self.assertEqual(device['group'], 'eero')
            elif device['name'] == 'Eero Beacon Family Room':
                self.assertEqual(device['mac'], '18:90:88:29:2b:5b')
                self.assertEqual(device['group'], 'eero')
            elif device['name'] == 'Kitchen Appliances Fridge':
                self.assertEqual(device['mac'], '68:a4:0e:2d:9a:91')
                self.assertEqual(device['group'], 'kitchen_appliances')

    def test_load_good_yaml(self):
        """Test well-formed YAML load."""
        known_devices_loader = KnownDevicesLoader()
        devices = list(known_devices_loader.load_from_string(TestKnownDevicesLoader.generate_test_data()))
        self.inspect_output(devices)

    def test_load_bad_yaml(self):
        """Test invalid YAML load."""
        bad_yaml = "Not YAML at all\n"
        known_devices_loader = KnownDevicesLoader()
        self.assertRaises(ValueError, lambda data : list(known_devices_loader.load_from_string(data)), bad_yaml)

    def test_load_file_not_found(self):
        """Test load with file that does not exist."""
        known_devices_loader = KnownDevicesLoader(filename="/does/not/exist.yml")
        devices = known_devices_loader.load()
        self.assertEqual(len(devices), 0)

    def test_load_good_yaml_from_file(self):
        """Test well-formed YAML load from file."""
        # pylint: disable=consider-using-with
        temp_file = tempfile.NamedTemporaryFile()
        with open(temp_file.name, 'w', encoding='utf8', newline='') as yaml_fp:
            yaml_fp.write(TestKnownDevicesLoader.generate_test_data())
            yaml_fp.close()
            known_devices_loader = KnownDevicesLoader(filename=temp_file.name)
            devices = known_devices_loader.load()
            self.inspect_output(devices)

    def test_load_bad_yaml_from_file(self):
        """Test invalid YAML load from file."""
        # pylint: disable=consider-using-with
        temp_file = tempfile.NamedTemporaryFile()
        with open(temp_file.name, 'w', encoding='utf8', newline='') as yaml_fp:
            yaml_fp.write('Not YAML at all')
            yaml_fp.close()
            known_devices_loader = KnownDevicesLoader(filename=temp_file.name)
            self.assertRaises(ValueError, known_devices_loader.load)
