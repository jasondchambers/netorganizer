import ipaddress

# pylint: disable=missing-class-docstring
class NetworkIsOutOfSpace(Exception):
    pass

class Ipv4PrivateNetworkSpace :
    """IPv4 private network space."""

    def __init__(self, cidr) :
        ip_network = ipaddress.ip_network(cidr)
        if not ip_network.is_private:
            raise ValueError("CIDR must be in the private space")
        self.__cidr = cidr
        self.__address_set = { format(item) for item in ip_network.hosts() }
        self.__used_set = set()

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
        if not ip_address in self.__address_set:
            raise ValueError(f'specified ip_address not in {self.__cidr}')
        if ip_address in self.__used_set:
            raise ValueError("specified ip_address already in use")
        self.__used_set.add(ip_address)
        return ip_address

    def get_address_set(self) -> list:
        """Return the set of all IPv4 addresses the space."""
        return self.__address_set

    def get_used_set(self):
        """Return the set of IPv4 addresses that have been allocated."""
        return self.__used_set

    def get_unused_set(self) :
        """Return the set of IPv4 addresses that are available to be allocated."""
        return self.__address_set - self.__used_set

class NetworkMapper :
    """Map the device table to the network space."""
    def __init__(self, vlan_subnet, device_table) -> None:
        self.__network_space = Ipv4PrivateNetworkSpace(vlan_subnet)
        self.__device_table = device_table

    def map_to_network_space(self) -> None:
        # pylint: disable=invalid-name
        for ip in self.__find_ips() :
            self.__network_space.allocate_specific_address(ip)
        for mac in self.__find_macs_needing_ip() :
            self.__assign_ip(mac)

    def get_network_space(self) -> Ipv4PrivateNetworkSpace:
        return self.__network_space

    def __find_ips(self) -> list:
        """Generate a list of IPs from the device table."""
        # pylint: disable=invalid-name
        df = self.__device_table.df
        return df.query("ip != ''")['ip'].tolist()

    def __find_macs_needing_ip(self) -> list:
        """Generate a list of MACs that do not have an IP."""
        # pylint: disable=invalid-name
        df = self.__device_table.df
        return df.query("ip == ''")['mac'].tolist()

    def __assign_ip(self,mac) -> None:
        """Assign an IP address to a device identified by it's MAC."""
        # pylint: disable=invalid-name
        df = self.__device_table.df
        df.loc[df["mac"] == mac, "ip"] = self.__network_space.allocate_address()

