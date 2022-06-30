"""Tests for NetorgConfigurator."""

import unittest
from unittest.mock import patch, MagicMock
from configure import NetorgConfigurator

class NetorgConfiguratorTest(unittest.TestCase) :
    """Tests for NetorgConfigurator"""

    @staticmethod
    def get_fake_api_key() -> str:
        """Return a fake API key purely for testing."""
        return 'AN_API_KEY'

    @patch('configure.NetorgConfigurator.get_config')
    def test_save(self, mock_get_config):
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
        netorg_configurator.save()

