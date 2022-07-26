"""This is the main module for Netorg."""
import argparse
import sys
import merakidevicetableloaderfactory
from configure import NetorgConfigurator
from netorgmeraki import MerakiNetworkMapper
from netorgsna import SnaAdapter
from scan import NetorgScanner
from generate import NetorgGenerator

def load_device_table(config):
    """Load the device table."""
    device_table_loader = merakidevicetableloaderfactory.create(config)
    return device_table_loader.load_all()

def load_config():
    """Load the configuratil file."""
    configurator = NetorgConfigurator()
    configurator.load()
    return configurator.get_config()

def sna_is_configured(config):
    """Determine if Secure Network Analytics has been configured."""
    if 'sna.manager.host' in config:
        return True
    return False

def do_configure() -> None:
    """Perform configure."""
    print("Configure")
    configurator = NetorgConfigurator()
    configurator.generate()
    configurator.save()

def do_generate() -> None:
    """Perform generate (devices.yml)."""
    print("Generate")
    config = load_config()
    device_table = load_device_table(config)
    generator = NetorgGenerator(config, device_table)
    generator.generate()

def do_scan() -> None:
    """Perform scan."""
    print("Scan")
    config = load_config()
    device_table = load_device_table(config)
    scanner = NetorgScanner(device_table)
    scanner.run()
    scanner.report()

def do_organize() -> None:
    """Perform organize."""
    print("Organize")
    config = load_config()
    device_table = load_device_table(config)
    generator = NetorgGenerator(config, device_table)
    generator.generate()
    meraki_network_mapper = MerakiNetworkMapper(config, device_table)
    meraki_network_mapper.update_fixed_ip_reservations()

def do_devicetable() -> None:
    """Perform devicetable (export)."""
    print("Export the device table")
    config = load_config()
    device_table = load_device_table(config)
    print(device_table.df.to_csv())

def do_push_changes_to_sna() -> None:
    """Perform push changes to SNA."""
    print("Pushing changes to Secure Network Analytics")
    config = load_config()
    if not sna_is_configured(config):
        print("Secure Network Analytics is not configured. Re-run with -c to configure.")
    else:
        print("Pushing changes to Secure Network Analytics")
        device_table = load_device_table(config)
        sna_adapter = SnaAdapter(config)
        sna_adapter.sync_with(device_table.df)

def main():
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
