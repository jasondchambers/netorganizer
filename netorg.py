"""This is the main module for Netorg."""
import argparse
from configure import NetorgConfigurator

def main():
    """Figure out what the user wants to happen and make it so."""
    parser = argparse.ArgumentParser(description='Organize your network.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--configure", help="[Re-]Configure Netorg", action="store_true")
    group.add_argument("-r", "--report", help="Produce a device report", action="store_true")
    args = parser.parse_args()
    configurator = NetorgConfigurator()
    configurator.generate()
    configurator.save()
    #if args.configure:
        #print("Configure")
        #configurator = NetorgConfigurator()
    #elif args.report:
        #print("Report")
    #else:
        #print("Organize")

if __name__ == "__main__":
    main()
