"""Tests for NetorgConfigurator."""

import unittest
from unittest.mock import patch
from configure import NetorgConfigurator

class NetorgConfiguratorTest(unittest.TestCase) :
    """Tests for NetorgConfigurator"""

    @patch('configure.NetorgConfigurator.get_config')
    def test_save_and_load(self, mock_get_config):
        """Test NetorgConfigurator.save() and load()"""
        netorg_configurator = NetorgConfigurator()
        mock_get_config.return_value = {
            "api_key": "12345",
            "devices_yml": "/a/b/devices.yml",
            "org_id": "5678",
            "network_id": "L_8979739588",
            "serial_id": "Q2MM-PL55-BYJY",
            "vlan_id": 1,
            "vlan_subnet": "192.168.128.0/24"
        }
        # TODO - take a backup copy of any existing config
        netorg_configurator.save()
        netorg_configurator2 = NetorgConfigurator()
        netorg_configurator2.load()
        # TODO - Restore backup copy of any existing config
        self.assertDictEqual(mock_get_config.return_value,netorg_configurator2.config)
