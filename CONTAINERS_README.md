# Running Net Organizer in a container

### 1. Installation

Ensure the environment variable $CNETORG_CONFIG_HOME is set. This is where the configuration file and the devices.yml will be stored. When you run the container, the path inside the container /home/netorg will be mapped to this directory.

Ensure Docker is installed.

You will also need to ensure the directory where Net Organizer resides is in the $PATH.

### 2. Build the Docker image

Ensure you are in the directory where Net Organizer resides and build as follows:

```text
$ docker build -t netorganizer .
```

### 3. Run as a container

The command cnetorg is to be used instead of netorg to run it in a container. Simply run as follows to test:

```text
$ cnetorg
usage: netorg.py [-h] [-c | -g | -s | -o | -d | -p]

Organize your network.

optional arguments:
  -h, --help            show this help message and exit
  -c, --configure       [Re-]Configure Netorg
  -g, --generate        Generate/update a devices.yml
  -s, --scan            Scan to see what's active, known, reserved
  -o, --organize        Organize the network
  -d, --devicetable     Export the device table
  -p, --pushchangestosna
                        Push grouping changes to Secure Network Analytics
```
