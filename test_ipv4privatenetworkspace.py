import unittest
from ipv4privatenetworkspace import Ipv4PrivateNetworkSpace
from ipv4privatenetworkspace import NetworkIsOutOfSpace

class TestIpv4PrivateNetworkSpace(unittest.TestCase):
    def test_invalid_cidr(self) :
        self.assertRaises(ValueError, Ipv4PrivateNetworkSpace, "x.x.x.x")
        
    def test_cidr_has_host_bits_set(self) :
        self.assertRaises(ValueError, Ipv4PrivateNetworkSpace, "192.168.128.22/24")
    
    def test_public_cidr(self) :
        self.assertRaises(ValueError, Ipv4PrivateNetworkSpace, "8.0.0.0/8")
    
    def test_end_to_end(self) :
        network_space = Ipv4PrivateNetworkSpace("192.168.128.252/30")
        self.assertEqual(2,len(network_space.get_address_set()), "Expected address_set to be size 2")
        self.assertIn('192.168.128.253', network_space.get_address_set())
        self.assertIn('192.168.128.254', network_space.get_address_set())
        self.assertEqual(0, len(network_space.get_used_set()), "Expected used_set to be size 0")
        self.assertEqual(2, len(network_space.get_unused_set()), "Expected unused_set to be size 2")
        self.assertIn('192.168.128.253', network_space.get_unused_set(), "Expected unused_set to contain 192.168.128.253")
        self.assertIn('192.168.128.254', network_space.get_unused_set(), "Expected unused_set to contain 192.168.128.254")
        allocated_address = network_space.allocate_address()
        self.assertEqual(1, len(network_space.get_used_set()), "Expected used_set to be size 1")
        allocated_address = network_space.allocate_address()
        self.assertEqual(2, len(network_space.get_used_set()), "Expected used_set to be size 2")
        self.assertEqual(0, len(network_space.get_unused_set()), "Expected used_set to be size 0")
        self.assertRaises(NetworkIsOutOfSpace, network_space.allocate_address)
    
    def test_allocate_specific_address(self) :
        network_space = Ipv4PrivateNetworkSpace("192.168.128.252/30")
        self.assertRaises(ValueError, network_space.allocate_specific_address, "8.8.8.8") # Not in CIDR
        allocated_address = network_space.allocate_specific_address("192.168.128.254")
        self.assertEqual('192.168.128.254', allocated_address, "Expected allocate_address to return 192.168.128.254")
        self.assertRaises(ValueError, network_space.allocate_specific_address, "192.168.128.254") # Already in use

