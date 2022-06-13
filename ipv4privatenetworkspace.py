import ipaddress

class NetworkIsOutOfSpace(Exception):
    pass

class Ipv4PrivateNetworkSpace :
    
    def __init__(self,cidr) :
        self.cidr = cidr
        self.ip_network = ipaddress.ip_network(cidr)
        if not self.ip_network.is_private: raise ValueError("CIDR must be in the private space")
        self.address_set = { format(item) for item in self.ip_network.hosts() }
        self.used_set = set()
    
    def get_address_set(self) :
        return self.address_set
    
    def get_used_set(self) :
        return self.used_set
    
    def get_unused_set(self) :
        return self.address_set - self.used_set
    
    def allocate_address(self) :
        try:
            return_address = self.get_unused_set().pop()
            self.used_set.add(return_address)
            return return_address
        except KeyError:
            raise NetworkIsOutOfSpace()
            
    def allocate_specific_address(self, ip_address) :
        if not ip_address in self.address_set: raise ValueError(f'specified ip_address not in {self.cidr}')
        if ip_address in self.used_set: raise ValueError("specified ip_address already in use")
        self.used_set.add(ip_address)
        return ip_address

