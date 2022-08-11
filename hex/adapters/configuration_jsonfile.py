
import json
import os
from ports import NetorgConfigurationPort

class NetorgConfigurationJsonFileAdapter(NetorgConfigurationPort):
    """Configuration file adapter where the config file is JSON in the home directory."""
    
    # overriding abstract method
    def load(self) -> dict:
        """Load configuration from a JSON file in the home directory."""
        config_filename = self.__get_config_filename()
        print(f'Loading config file {config_filename}')
        with open(config_filename, encoding='utf8') as json_file:
            return json.load(json_file)

    # overriding abstract method
    def save(self,config: dict):
        """Save configuration."""
        if config:
            config_filename = self.__get_config_filename()
            print(f'Saving config file {config_filename}')
            with open(config_filename, 'w', encoding='utf8') as netorg_config_file:
                netorg_config_file.write(json.dumps(config, indent=2))

    def __get_config_filename(self) -> str:
        """Return the fully qualified config filename e.g. /a/b/.netorg.cfg"""
        directory = os.path.expanduser('~')
        filename = '.netorg.cfg'
        return os.path.join(directory,filename)