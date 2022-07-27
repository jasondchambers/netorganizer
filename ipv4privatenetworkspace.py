"""Module for managing an IPv4 private address space."""
import ipaddress

# pylint: disable=missing-class-docstring
class NetworkIsOutOfSpace(Exception):
    pass

class Ipv4PrivateNetworkSpace :
    """IPv4 private network space."""

    def __init__(self, cidr) :
        self.cidr = cidr
        self.ip_network = ipaddress.ip_network(cidr)
        if not self.ip_network.is_private:
            raise ValueError("CIDR must be in the private space")
        self.__address_set = { format(item) for item in self.ip_network.hosts() }
        self.__used_set = set()

    def get_address_set(self) -> list:
        """Return the set of all IPv4 addresses the space."""
        return self.__address_set

    def get_used_set(self):
        """Return the set of IPv4 addresses that have been allocated."""
        return self.__used_set

    def get_unused_set(self) :
        """Return the set of IPv4 addresses that are available to be allocated."""
        return self.__address_set - self.__used_set

    def allocate_address(self) :
        """Allocate an IP address."""
        try:
            return_address = self.get_unused_set().pop()
            self.__used_set.add(return_address)
            return return_address
        except KeyError as exc:
            raise NetworkIsOutOfSpace() from exc

    def allocate_specific_address(self, ip_address) :
        """Allocate a specific IP address."""
        if ip_address not in self.__address_set:
            raise ValueError(f'specified ip_address not in {self.cidr}')
        if ip_address in self.__used_set:
            raise ValueError("specified ip_address already in use")
        self.__used_set.add(ip_address)
        return ip_address
