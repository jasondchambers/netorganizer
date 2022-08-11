from typing import NamedTuple
from abc import ABC, abstractmethod
from typing import List
import requests

from devicetable import DeviceTable

class KnownDevice(NamedTuple):
    name: str
    mac: str
    group: str

    def __str__(self) -> str:
        return f'Known device: {self.name} with MAC {self.mac} in {self.group}'

class ActiveClient(NamedTuple):
    mac: str
    name: str
    description: str
    ip_address: str

    def __str__(self) -> str:
        return f'Active client: {self.name} {self.description} with MAC {self.mac} has IP address {self.ip_address}'

class FixedIpReservation(NamedTuple):
    mac: str
    name: str
    ip_address: str

    def __str__(self) -> str:
        return f'Fixed IP reservation: {self.mac} {self.name} {self.ip_address}'

class KnownDevicesPort(ABC): #DONE

    @abstractmethod
    def load() -> List[KnownDevice]: #DONE
        pass

    @abstractmethod
    def save(device_table: DeviceTable) -> None: #DONE
        pass

class ActiveClientsPort(ABC): #DONE

    @abstractmethod
    def load() -> List[ActiveClient]: #DONE
        pass

class FixedIpReservationsPort(ABC): #DONE

    @abstractmethod
    def load() -> List[FixedIpReservation]: #DONE
        pass

    @abstractmethod
    def save(device_table: DeviceTable) -> None: #DONE
        pass

class NetorgConfigurationPort(ABC):

    @abstractmethod
    def load() -> dict: #DONE
        pass

    @abstractmethod
    def save(config: dict): #DONE
        pass

class ConfigurationWizardPort(ABC):

    @abstractmethod
    def generate() -> dict:
        pass

class DeviceTableCsvOutPort(ABC): #DONE

    @abstractmethod
    def write(device_table_csv: str): #DONE
        pass

class SecureNetworkAnalyticsHostGroupManagementPort(ABC): #TODO

    @abstractmethod
    def update_host_groups(device_table: DeviceTable) -> None: #TODO
        pass

    class FailedToCreateHostGroup(Exception) :
        pass

    class FailedToUpdateHostGroup(Exception) :
        pass

    class FailedToDeleteHostGroup(Exception) :
        pass

class SecureNetworkAnalyticsSessionPort(ABC):

    @abstractmethod
    def login(host: str, user: str, password: str) -> None:
        pass

    @abstractmethod
    def logout() -> None:
        pass

    @abstractmethod
    def get_host() -> str:
        pass

    @abstractmethod
    def get_tenant_id() -> str:
        pass

    @abstractmethod
    def get_api_session() -> requests.Session:
        pass

    class FailedToLogin(Exception) :
        pass