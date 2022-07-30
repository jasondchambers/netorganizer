"""Tests for netorgsna.py."""
import unittest

from netorgsna import SnaHostGroupManager

class TestSnaHostGroupManager(unittest.TestCase) :
    """Tests for SnaHostGroupManager."""

    # Test data to mimic:
    # https://{host}/smc-configuration/rest/v1/tenants/{tenant_id}/tags/tree'
    hostgroup_tree = [{
        'root': [
            {
                'id': 1,
                'name': 'Inside Hosts',
                'children': [
                    {
                        'id': 23,
                        'name': 'By Function',
                        'children': []
                    },
                    {
                        'id': 50132,
                        'name': 'Net Organizer Groups',
                        'children': [
                            {
                                'id': 50134,
                                'name': 'Eero',
                                'children': []
                            },
                            {
                                'id': 50133,
                                'name': 'Lights',
                                'children': []
                            },
                            {
                                'id': 50136,
                                'name': 'Ring',
                                'children': []
                            },
                            {
                                'id': 50135,
                                'name': 'Speakers',
                                'children': []
                            }
                        ],
                    }
                ]
            }
        ]}
    ]

    # Test data to mimic response from:
    # url = f'https://{host}/smc-configuration/rest/v1/tenants/{tenant_id}/tags'
    tags = [
      {
        "name" : "Outside Hosts",
        "id" : 0
      }, {
        "name" : "Inside Hosts",
        "id" : 1
      }, {
        "name" : "Servers",
        "id" : 2
      }, {
        "name" : "SMS Servers",
        "id" : 50
      }, {
        "name" : "Load Balancer VIPs",
        "id" : 50079
      }, {
        "name" : "Internal Facing Load Balancer VIPs",
        "id" : 50080
      }, {
        "name" : "Net Organizer Groups",
        "id" : 50132
      }, {
        "name" : "Catch All",
        "id" : 65534
      }
    ]

    def test_analyze_changes(self):
        """Test SnaHostGroupManager.analyze_changes()."""
        current_hostgroups = {
            'Eero': ['192.168.128.11', '192.168.128.12'],
            'Lights': ['192.168.128.10'],
            'Ring': ['192.168.128.15', '192.168.128.16'],
            'Speakers': ['192.168.128.13', '192.168.128.14']
        }
        new_hostgroups = {
            'Lights': ['192.168.128.10', '192.168.128.191', '192.168.128.192'],
            'Eero': ['192.168.128.11'],
            'Ring': ['192.168.128.15', '192.168.128.16', '192.168.128.17'],
            'Laptops': ['192.168.128.190']
        }
        sna_hostgroup_manager = SnaHostGroupManager(None)
        sna_hostgroup_manager.analyze_changes(current_hostgroups,new_hostgroups)
        self.assertEqual(1,len(sna_hostgroup_manager.hostgroups_to_create_set))
        self.assertIn('Laptops', sna_hostgroup_manager.hostgroups_to_create_set)
        self.assertEqual(3,len(sna_hostgroup_manager.hostgroups_to_update_set))
        self.assertIn('Eero', sna_hostgroup_manager.hostgroups_to_update_set)
        self.assertIn('Lights', sna_hostgroup_manager.hostgroups_to_update_set)
        self.assertIn('Ring', sna_hostgroup_manager.hostgroups_to_update_set)
        self.assertEqual(1,len(sna_hostgroup_manager.hostgroups_to_delete_set))
        self.assertIn('Speakers', sna_hostgroup_manager.hostgroups_to_delete_set)

    def test_analyze_changes_update(self):
        current_hostgroups = {
            'lights': [
                '192.168.129.61', 
                '192.168.129.21',
                '192.168.129.223',
                '192.168.129.33',
                '192.168.129.117'],
            'unclassified': [
                '192.168.128.61', 
                '192.168.128.21',
                '192.168.128.223',
                '192.168.128.33',
                '192.168.128.117']
        }
        new_hostgroups = {
            'lights': [
                '192.168.129.61', 
                '192.168.129.21',
                '192.168.129.223',
                '192.168.129.33',
                '192.168.129.170'], # Changed
            'unclassified': [
                '192.168.128.61', 
                '192.168.128.21',
                '192.168.128.223',
                '192.168.128.33',
                '192.168.128.170'] # Changed
        }
        sna_hostgroup_manager = SnaHostGroupManager(None)
        sna_hostgroup_manager.analyze_changes(current_hostgroups,new_hostgroups)
        self.assertEqual(0,len(sna_hostgroup_manager.hostgroups_to_create_set))
        self.assertEqual(2,len(sna_hostgroup_manager.hostgroups_to_update_set))
        self.assertIn('unclassified', sna_hostgroup_manager.hostgroups_to_update_set)
        self.assertIn('lights', sna_hostgroup_manager.hostgroups_to_update_set)

    def test_get_group_children(self):
        """Test SnaHostGroupManager.get_group_children()."""
        inside_host_children = SnaHostGroupManager.get_group_children(
            TestSnaHostGroupManager.hostgroup_tree[0]['root'],hostgroup_id=1)
        net_org_hostgroup_children = SnaHostGroupManager.get_group_children(
            inside_host_children,50132)
        self.assertEqual(len(net_org_hostgroup_children),4)

    def test_find_hostgroup_id_in_tags_data(self):
        """Test SnaHostGroupManager.find_hostgroup_id_in_tags_data()."""
        inside_hosts_id = SnaHostGroupManager.find_hostgroup_id_in_tags_data(
            TestSnaHostGroupManager.tags,'Inside Hosts')
        self.assertEqual(1,inside_hosts_id)

    def test_build_hostgroup_name_to_id_map(self):
        """Test SnaHostGroupManager.build_hostgroup_name_to_id_map()."""
        inside_host_children = SnaHostGroupManager.get_group_children(
            TestSnaHostGroupManager.hostgroup_tree[0]['root'],hostgroup_id=1)
        net_org_hostgroup_children = SnaHostGroupManager.get_group_children(
            inside_host_children,50132)
        hostgroup_name_to_id_map = SnaHostGroupManager.build_hostgroup_name_to_id_map(
            net_org_hostgroup_children)
        expected = {'Eero': 50134, 'Lights': 50133, 'Ring': 50136, 'Speakers': 50135}
        self.assertDictEqual(expected, hostgroup_name_to_id_map)
