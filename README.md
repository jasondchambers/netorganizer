# Net Organizer

Not yet releasable. Still very much under development!

Network Organizer enables you to bring some order to the chaos that might be your network. You could make the case that it is a lightweight IP Address Manager (IPAM). It enables you to take inventory of active hosts and to neatly classify each of them into groups. It will also manage fixed IP reservations for you. It can convert a dynamic IP or allocate a new fixed IP reservation for registered hosts that do not have one. It can clean up lingering fixed IP reservations for un-registered and in-active hosts. It can bring to your attention un-registered hosts that are active on your network and invite you to register and classify them. 

Along the way, it avoids network collisions and avoids disruptive re-mapping of the network space.

Once hosts are classifed, you can export the device details for use by other tools - for example, Cisco Secure Network Analytics.

## Usage

The --configure feature is required to get started and is also used if there are changes to the network configuration or API key.
```bash
$ netorg --configure
```

The --generate feature is used to generate the devices.yml file containing registered devices. This step can be re-run to update the devices.yml file taking into account any new devices that may have joined the network since the file was generated.
```bash
$ netorg --generate
```

The --scan feature merely analyzes active devices on the network, the registered devices in the devices.yml and fixed IP reservations. It reports on what it finds but doesn't take any action.
```bash
$ netorg --scan
```

The --organize feature performs a scan and executes any actions based on the findings from the scan. For example, fixed IP reservations that are no longer needed are removed. New fixed IP reservations are created where necessary. Devices are registered in the devices.yml if they do not exist yet are active.
```bash
$ netorg --organize
```

## Terminology

A __device__ is a host on the network. A Smart TV or a laptop are examples of devices.

A __device__ is uniquely identified by it's MAC address. Note that MAC randomization has become popular with various devices to enhance privacy. MAC address randomization is an effective way to maintain privacy in public settings, where you don’t know who is looking at your connectivity and location history. But it does create challenges for managing your own network. It is recommended to turn off this feature when connecting to your own managed network, but by all means use the feature when joining public WiFi.

There are 3 primary states for __device__. The states are __registered__, __active__ and __reserved__ and are described below. Note that these states are NOT mutually exclusive. For example, a __device__ could be __registered__ and __active__ but not __reserved__. Therefore, the total number of possible states a __device__ could be in is 7 (2 ^ 3 - 1). 

A __device__ can be __registered__ by you. Registered devices are known devices on your network. Registered devices are configured in a simple YAML text file. You may classify similar devices under a group - whatever makes sense for your network. Registered devices may be unclassified - you can manually classify these later. 

A __device__ can be __active__ on the network. This means it has a current DHCP lease and therefore has an IP address.

A __device__ can be __reserved__ where it has a fixed IP reservation. This means it is granted the same static IP address each time it joins the network. 

## How to get started

### 1. Pre-installation

You will need to obtain a Meraki API key. See the following for details:
https://developer.cisco.com/meraki/api-v1/#!authorization/obtaining-your-meraki-api-key

Record the API key somewhere as you will be prompted for it during subsequent phases of the installation and configuration of netorganizer.

### 2. Installation

This has been developed and tested for Python 3.10.5. Earlier versions may not work. Python 2 will certainly not work. All pip packages are installed in a separate virtual environment (venv). 

Ensure the environment variable $NETORG_HOME is set to the directory where netorganizer is located.

Ensure the PATH includes $NETORG_HOME.

Run the install.sh script as follows:

```shell
$ ./install.sh
```

### 3. Configuration

To get started, you will need to generate a netorg configuration file. It's just a JSON text file that resides in the user's home directory. Rather than create one by hand, you can generate one using the --configure flag as follows:

```text
$ netorg --configure
Configure
You will need to obtain an API key. See the following for details:
https://developer.cisco.com/meraki/api-v1/#!authorization/obtaining-your-meraki-api-key
Meraki API key: 
Multiple networks found:
1 - Nottingham Office
2 - Mobile devices
Which network? : 1
Multiple devices found:
1 - MX68 - Q2KY-XXXX-XXXX
2 - MS120-8LP - Q2BX-XXXX-XXXX
Which device? : 1
Multiple VLANs found:
1 - Default - 192.168.128.0/24
2 - Lab - 192.168.4.0/24
3 - Guest - 192.168.5.0/24
Which VLAN? : 1
Directory for where to find/store registered devices [/Users/bob/netorganizer]: 
Filename for where to find/store registered devices [devices.yml]: 
Saving config file /Users/bob/.netorg.cfg
```

You shouldn't need to reconfigure netorganizer again unless you rotate your Meraki API Key and/or modify your network in anyway (e.g. different network settings, subnets, vlans, devices).

### 4. Generate devices.yml

Registered devices are devices known to you. They could be your smart phones, TVs, thermostats, speakers, appliances, tablets and of course laptops and PCs.

To register a device, you will need to capture the MAC address, provide a name for the device and classify it under a grouping. This is to be stored in a file called devices.yml. The devices.yml has to be valid [YAML](https://yaml.org).

You don't need to write the devices.yml file from scratch. One can be generated for you to get you started based on devices that are currently active. There is no automated classification feature yet, and so it will put all the un-classified active devices it finds under "unclassified". You can classify them later if required.

Here's an example:
```yaml
---
devices:
  unclassified:
    - None,9a:1b:ba:d4:b6:54
    - RingCamMini-11,34:3e:a4:4e:1b:11
    - Craigs-iPhone,6e:d9:36:a9:21:ee
```

You should consider classifying the devices as you see fit by editing the devices.yml file. Below is an example containing classified devices:

```yaml
---
devices:
  servers:
    - Servers Linux,f8:63:3f:19:b5:36
  printers:
    - Printers Office,00:1b:a9:1a:82:d4
    - Printers Basement,64:6c:80:8e:c5:1c
  eero:
    - Eero Beacon Lady Pit,18:90:88:28:eb:5b
    - Eero Beacon Family Room,18:90:88:29:2b:5b
    - Eero Office,f8:bc:0e:01:29:32
    - Eero Beacon Dining Room,30:57:8e:f8:84:bb
  kitchen_appliances:
    - Kitchen Appliances Fridge,68:a4:0e:2d:9a:91
```

A devices.yml file can be generated as follows:

```text
$ netorg --generate
```

It saves off the generated devices.yml in the directory you specified during the configuration.
If a devices.yml already exists, it merely updates it.

### 4. Perform a scan

The scan feature merely analyzes active devices on the network, the registered devices in the devices.yml and fixed IP reservations. 

Here is an example:

```text
1 device(s) are active, not reserved and not registered. These will be registered as unclassified and assigned a reserved IP at the next sync:
     Aura-6141
1 device(s) are reserved, not active and not registered. The reserved IP will be removed at the next sync:
     Jimmys Devices iPhone
3 device(s) are active, reserved and not registered. These will be registered as un-classified at the next sync:
     Smart Lighting Bar Light 1
     Roses Devices MacBook
     SONOS Connect CD
1 device(s) are registered, not reserved and not active. A reserved IP will be created at the next sync:
     Webcam
11 device(s) are registered, active and not reserved. The current IP will be converted to a static IP at the next sync:
     None
     RingCamMini-11
     JASCHAMB-M-XRDP
     None
     HS105
     HS105
     eero-20:be:cd:ac:37:20
     LT6221
     RingCamMini-d7
     None
     stratford-switch-0c8ddb0403b6
14 device(s) are active and unclassified. You should consider classifying them before the next sync:
     None
     Roses Devices Kindle
     SONOS Den
     Ring base station
     Echos Kitchen Echo Show
     RingCamMini-11
     Apple TVs K and J room
     SONOS Bridge
     SONOS Port HiFi
     Eero Beacon Dining Room
     Ring front door
     Jasons Devices iMac
     Arlo Camera
     Echos Bar
     SONOS Den LS
```
# Supports

1. Cisco Meraki powered networks only (for now)
2. IPv4 only (for now)

# Internals

![UML](netorg.png)