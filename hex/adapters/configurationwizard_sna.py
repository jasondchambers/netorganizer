import getpass
from ports import ConfigurationWizardPort, SecureNetworkAnalyticsSessionPort

class ConfigurationWizardForSnaConsoleAdapter(ConfigurationWizardPort):

    def __init__(self, sna_session_port: SecureNetworkAnalyticsSessionPort):
        self.__sna_session_port = sna_session_port

    # overriding abstract method
    def generate(self) -> dict:
        """Generate Secure Network Analytics config."""
        config = {}
        while True:
            answer = input('Do you want to configure Secure Network Analytics? (y/n) [n]:')
            if not answer or answer == 'n' or answer == 'N':
                break
            if answer in ('y', 'Y'):
                config['sna.manager.host'] = input('Manager host: ')
                config['sna.manager.username'] = input('Manager username: ')
                config['sna.manager.password'] = getpass.getpass('Manager password: ')
                if self.__isvalid_sna_config(config):
                    break
                config = {}
        return config

    def __isvalid_sna_config(self, config) -> bool:
        """Return true if the SNA config is valid."""
        # pylint: disable=line-too-long
        try:
            self.__sna_session_port.login(
                config['sna.manager.host'],
                config['sna.manager.username'], 
                config['sna.manager.password'])
            self.__sna_session_port.logout()
            print('Secure Network Analytics configuration is valid')
            return True
        except SecureNetworkAnalyticsSessionPort.FailedToLogin as e:
            print(f'Failed to login to Secure Network Analytics Manager at {config["sna.manager.host"]}')
            return False