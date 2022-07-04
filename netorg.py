"""This is the main module for Netorg."""
import argparse
from configure import NetorgConfigurator
from report import NetorgReporter
from generate import NetorgGenerator

def main():
    """Figure out what the user wants to happen and make it so."""
    parser = argparse.ArgumentParser(description='Organize your network.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--configure", help="[Re-]Configure Netorg", action="store_true")
    group.add_argument("-g", "--generate", help="Generate/update a devices.yml", action="store_true")
    group.add_argument("-r", "--discover", help="Produce a device report", action="store_true")
    args = parser.parse_args()
    if args.configure:
        print("Configure")
        configurator = NetorgConfigurator()
        configurator.generate()
        configurator.save()
    elif args.generate:
        print("Generate")
        configurator = NetorgConfigurator()
        configurator.load()
        config = configurator.get_config()
        generator = NetorgGenerator(config)
        generator.generate()
    elif args.report:
        print("Report")
        configurator = NetorgConfigurator()
        configurator.load()
        config = configurator.get_config()
        reporter = NetorgReporter(config)
        print(reporter.device_table)
    else:
        print("Organize")

if __name__ == "__main__":
    main()
