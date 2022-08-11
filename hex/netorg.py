"""This is the main module for Netorg."""
import argparse
import sys
from adapters.activeclients_meraki import ActiveClientsMerakiAdapter
from adapters.configuration_jsonfile import NetorgConfigurationJsonFileAdapter
from adapters.configurationwizard import ConfigurationWizardConsoleAdapter
from adapters.configurationwizard_sna import ConfigurationWizardForSnaConsoleAdapter
from adapters.devicetableout_console import DeviceTableCsvOutConsoleAdapter
from adapters.fixedipreservations_meraki import FixedIpReservationsMerakiAdapter
from adapters.knowndevices_yamlfile import KnownDevicesYamlFileAdapter
from adapters.sna_hostgroups import SecureNetworkAnalyticsHostGroupManagementAdapter
from adapters.sna_session import SecureNetworkAnalyticsSessionAdapter
from app import NetOrganizerApp

def create_net_organizer_app() -> NetOrganizerApp:
    net_organizer_configurator = NetorgConfigurationJsonFileAdapter()
    config = net_organizer_configurator.load()
    net_organizer_app = NetOrganizerApp(
        known_devices_port=KnownDevicesYamlFileAdapter(config),
        active_clients_port=ActiveClientsMerakiAdapter(config),
        fixed_ip_reservations_port=FixedIpReservationsMerakiAdapter(config),
        device_table_csv_out_port=DeviceTableCsvOutConsoleAdapter(config),
        sna_hostgroup_port=SecureNetworkAnalyticsHostGroupManagementAdapter(
            config,
            sna_session_port=SecureNetworkAnalyticsSessionAdapter()
        )
    )
    return net_organizer_app

def do_configure() -> None:
    """Perform configure."""
    print("Configure")
    config_wizard = ConfigurationWizardConsoleAdapter()
    config = config_wizard.generate()
    config_wizard_for_sna = ConfigurationWizardForSnaConsoleAdapter(
        sna_session_port=SecureNetworkAnalyticsSessionAdapter())
    config_sna = config_wizard_for_sna.generate()
    merged = {**config,**config_sna}
    net_organizer_configurator = NetorgConfigurationJsonFileAdapter()
    net_organizer_configurator.save(merged)

def do_scan() -> None:
    """Perform scan."""
    print("Scan")
    net_organizer_app = create_net_organizer_app()
    net_organizer_app.do_scan()

def do_devicetable() -> None:
    """Perform devicetable (export)."""
    print("Export the device table")
    net_organizer_app = create_net_organizer_app()
    net_organizer_app.do_devicetable()

def do_generate() -> None:
    """Perform generate (devices.yml)."""
    print("Generate")
    net_organizer_app = create_net_organizer_app()
    net_organizer_app.do_save_known_devices()

def do_organize() -> None:
    """Perform organize."""
    print("Organize")
    net_organizer_app = create_net_organizer_app()
    net_organizer_app.do_organize()

def do_push_changes_to_sna() -> None:
    """Perform push changes to SNA."""
    print("Pushing changes to Secure Network Analytics")
    net_organizer_app = create_net_organizer_app()
    net_organizer_app.do_push_changes_to_sna()

def get_parser() -> argparse.ArgumentParser:
    """Figure out what the user wants to happen and make it so."""
    parser = argparse.ArgumentParser(description='Organize your network.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--configure", help="[Re-]Configure Netorg",
                       action="store_true")
    group.add_argument("-g", "--generate", help="Generate/update a devices.yml",
                       action="store_true")
    group.add_argument("-s", "--scan", help="Scan to see what's active, known, reserved",
                       action="store_true")
    group.add_argument("-o", "--organize", help="Organize the network",
                       action="store_true")
    group.add_argument("-d", "--devicetable", help="Export the device table",
                       action="store_true")
    group.add_argument("-p", "--pushchangestosna",
                       help="Push grouping changes to Secure Network Analytics",
                       action="store_true")
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.configure:
        do_configure()
    elif args.generate:
        do_generate()
    elif args.scan:
        do_scan()
    elif args.organize:
        do_organize()
    elif args.devicetable:
        do_devicetable()
    elif args.pushchangestosna:
        do_push_changes_to_sna()
    else:
        parser.print_help(sys.stderr)

if __name__ == "__main__":
    main()
