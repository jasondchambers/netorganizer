"""This is the main module for Netorg."""
import argparse
import sys
import merakidevicetableloaderfactory
from configure import NetorgConfigurator
from netorgmeraki import MerakiNetworkMapper
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
    args = parser.parse_args()
    if args.configure:
        print("Configure")
        configurator = NetorgConfigurator()
        configurator.generate()
        configurator.save()
    elif args.generate:
        print("Generate")
        config = load_config()
        device_table = load_device_table(config)
        generator = NetorgGenerator(config, device_table)
        generator.generate()
    elif args.scan:
        print("Scan")
        config = load_config()
        device_table = load_device_table(config)
        scanner = NetorgScanner(device_table)
        scanner.run()
        scanner.report()
    elif args.organize:
        print("Organize")
        config = load_config()
        device_table = load_device_table(config)
        generator = NetorgGenerator(config, device_table)
        generator.generate()
        meraki_network_mapper = MerakiNetworkMapper(config, device_table)
        meraki_network_mapper.update_fixed_ip_reservations()
    elif args.devicetable:
        print("Export the device table")
        config = load_config()
        device_table = load_device_table(config)
        print(device_table.df.to_csv())
    else:
        parser.print_help(sys.stderr)

if __name__ == "__main__":
    main()
