import unittest
from devicetable import DeviceTableBuilder 

class DeviceTableBuilderTest(unittest.TestCase):
    def test_all(self) :
        device_table_builder = DeviceTableBuilder()
        device_table_builder.set_details('aab', {'registered': False, 'reserved': False, 'active': True, 'ip': '192.168.128.10', 'group': '', 'name': 'JASCHAMB-M-XRDP'})
        device_table_builder.set_details('aba', {'registered': False, 'reserved': True, 'active': False, 'ip': '192.168.128.50', 'group': '', 'name': 'LT6221'})
        device_table_builder.set_details('abb', {'registered': False, 'reserved': True, 'active': True, 'ip': '192.168.128.51', 'group': '', 'name': 'HS105'})
        device_table_builder.set_details('baa', {'registered': True, 'reserved': False, 'active': False, 'ip': '', 'group': 'printers', 'name': 'Aura-6141'})
        device_table_builder.set_details('bab', {'registered': True, 'reserved': False, 'active': True, 'ip': '192.168.128.11', 'group': 'printers', 'name': 'Office'})
        device_table_builder.set_details('bba', {'registered': True, 'reserved': True, 'active': False, 'ip': '192.168.128.100', 'group': 'laptops', 'name': 'Jason'})
        device_table_builder.set_details('bbb', {'registered': True, 'reserved': True, 'active': True, 'ip': '192.168.128.101', 'group': 'laptops', 'name': 'Rose'})
        device_table = device_table_builder.build()