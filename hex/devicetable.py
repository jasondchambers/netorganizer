"""All the things associated with Loading, building and accessing a device table."""
import pandas as pd
from pandas import DataFrame

class DeviceTable :
    """The device table is the heart of Network Organizer."""
    def __init__(self,data) -> None:
        # pylint: disable=invalid-name
        self.df = pd.DataFrame(data)

