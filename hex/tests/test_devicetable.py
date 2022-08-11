from typing import List
import unittest
from devicetable import DeviceTable
from devicetableloader import DeviceTableLoader
from ports import ActiveClient, ActiveClientsPort, DeviceTableCsvOutPort, FixedIpReservation, FixedIpReservationsPort, KnownDevice, KnownDevicesPort

# Test table
#
#   known | reserved (IP) | active | Description                | Action
# ==============+===============+========+======================+=======
#       0 |             0 |      0 |                            |
# aab   0 |             0 |      1 | active                     | register the device
# aba   0 |             1 |      0 | reserved                   | remove reservation
# abb   0 |             1 |      1 | reserved & active          | register the device
# baa   1 |             0 |      0 | known                      | create reservation
# bab   1 |             0 |      1 | known & active             | convert to static reservation
# bba   1 |             1 |      0 | known & reserved           |
# bbb   1 |             1 |      1 | known & reserved & active  |
TEST_TABLE_SIZE = 7

class KnownDevicesTestAdapter(KnownDevicesPort):
    """Load known devices for test purporses."""

    list_of_known_devices: List[KnownDevice] = [
        KnownDevice(name='Meerkat',         mac='baa', group='servers'),
        KnownDevice(name='Office Printer',  mac='bab', group='printers'),
        KnownDevice(name='Front Doorbell',  mac='bba', group='security'),
        KnownDevice(name='Driveway camera', mac='bbb', group='security')
    ]

    # overriding abstract method
    def load(self) -> List[KnownDevice]:
        return self.list_of_known_devices

    def save(self,device_table: DeviceTableCsvOutPort) -> None:
        pass

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in KnownDevicesTestAdapter.list_of_known_devices]

class ActiveClientsTestAdapter(ActiveClientsPort):

    list_of_active_clients: List[ActiveClient] = [
        ActiveClient(mac='aab', name=None, description='HS105',           ip_address='192.168.128.201'),
        ActiveClient(mac='abb', name=None, description='HS105',           ip_address='192.168.128.202'),
        ActiveClient(mac='bab', name=None, description='Office Printer',  ip_address='192.168.128.203'),
        ActiveClient(mac='bbb', name=None, description='Driveway camera', ip_address='192.168.128.204')
    ]

    # overriding abstract method
    def load(self) -> List[ActiveClient]:
        return self.list_of_active_clients

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in ActiveClientsTestAdapter.list_of_active_clients]

class FixedIpReservationsTestAdapter(FixedIpReservationsPort):

    list_of_fixed_ip_reservations: List[FixedIpReservation] = [
        FixedIpReservation(mac='aba', ip_address='192.168.128.191', name='Work Laptop'),
        FixedIpReservation(mac='abb', ip_address='192.168.128.202', name='HS105'),
        FixedIpReservation(mac='bba', ip_address='192.168.128.191', name='Echo 1'),
        FixedIpReservation(mac='bbb', ip_address='192.168.128.204', name='Echo 2')
    ]

    # overriding abstract method
    def load(self) -> List[FixedIpReservation]: 
        return self.list_of_fixed_ip_reservations

    # overriding abstract method
    def save(self,device_table: DeviceTable) -> None: 
        pass

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in FixedIpReservationsTestAdapter.list_of_fixed_ip_reservations]

class TestDeviceTableLoader(unittest.TestCase) :
    """Test cases for DeviceTableLoader."""

    def test_load_known(self) :
        """Test loading of known devices."""
        device_table_loader = DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=None,
            fixed_ip_reservations_port=None
        )
        device_table_loader._DeviceTableLoader__load_known()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(len(KnownDevicesTestAdapter.list_of_known_devices),df.query("known").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_active(self) :
        """Test loading of active devices."""
        device_table_loader = DeviceTableLoader(
            known_devices_port=None,
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=None
        )
        device_table_loader._DeviceTableLoader__load_active_clients()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(0,df.query("known").shape[0])
        self.assertEqual(len(ActiveClientsTestAdapter.list_of_active_clients),df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_fixed_ip_reservations(self) :
        """Test loading of fixed IP reservations."""
        device_table_loader = DeviceTableLoader(
            known_devices_port=None,
            active_clients_port=None,
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        device_table_loader._DeviceTableLoader__load_fixed_ip_reservations()
        df = device_table_loader.device_table_builder.build().df
        self.assertEqual(0,df.query("known").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(len(FixedIpReservationsTestAdapter.list_of_fixed_ip_reservations),df.query("reserved").shape[0])

    def test_load_all(self) :
        """Test loading of all data."""
        device_table_loader = DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        df = device_table_loader.load_all().df
        self.assertEqual(TEST_TABLE_SIZE,df.shape[0])

        # known
        self.assertEqual(len(KnownDevicesTestAdapter.list_of_known_devices),df.query("known").shape[0])
        for mac in KnownDevicesTestAdapter.get_list_of_macs() :
            self.assertIn(mac,df.query("known")["mac"].tolist())

        # active
        self.assertEqual(len(ActiveClientsTestAdapter.list_of_active_clients),df.query("active").shape[0])
        for mac in ActiveClientsTestAdapter.get_list_of_macs() :
            self.assertIn(mac,df.query("active")["mac"].tolist())

        # reserved
        self.assertEqual(len(FixedIpReservationsTestAdapter.list_of_fixed_ip_reservations),df.query("reserved").shape[0])
        for mac in FixedIpReservationsTestAdapter.get_list_of_macs() :
            self.assertIn(mac,df.query("reserved")["mac"].tolist())

        ## known and active
        known_set = set(KnownDevicesTestAdapter.get_list_of_macs())
        active_set = set(ActiveClientsTestAdapter.get_list_of_macs())
        expected = known_set.intersection(active_set)
        actual = df.query("known and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # known and reserved
        reserved_set = set(FixedIpReservationsTestAdapter.get_list_of_macs())
        expected = known_set.intersection(reserved_set)
        actual = df.query("known and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # active and reserved
        expected = active_set.intersection(reserved_set)
        actual = df.query("active and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # known and reserved and active
        expected = known_set.intersection(reserved_set,active_set)
        actual = df.query("known and reserved and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))
