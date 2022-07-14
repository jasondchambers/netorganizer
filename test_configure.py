"""Tests for NetorgConfigurator."""

import os
import unittest
from unittest.mock import patch
from configure import NetorgConfigurator

class NetorgConfiguratorTest(unittest.TestCase) :
    """Tests for NetorgConfigurator"""

    @patch('configure.NetorgConfigurator.get_config_filename')
    @patch('configure.NetorgConfigurator.get_config')
    def test_save_and_load(self, mock_get_config, mock_get_config_filename):
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
        temp_config_file = ".tmp.netorg.cfg.for_testing"
        mock_get_config_filename.return_value = temp_config_file
        netorg_configurator.save()
        netorg_configurator2 = NetorgConfigurator()
        netorg_configurator2.load()
        self.assertDictEqual(mock_get_config.return_value,netorg_configurator2.config)
        os.remove(temp_config_file)
