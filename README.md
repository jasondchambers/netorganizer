# Net Organizer

Not yet releasable. Still very much under development!

Network Organizer enables you to bring some order to the chaos that might be your network. You could make the case that it is a lightweight IP Address Manager (IPAM). It enables you to take inventory of active hosts and to neatly classify each of them into groups. It will also manage fixed IP reservations for you. It can convert a dynamic IP or allocate a new fixed IP reservation for registered hosts that do not have one. It can clean up lingering fixed IP reservations for un-registered and in-active hosts. It can bring to your attention un-registered hosts that are active on your network and invite you to register and classify them. 

Along the way, it avoids network collisions and avoids disruptive re-mapping of the network space.

Once hosts are classifed, you can export the device details for use by other tools - for example, Cisco Secure Network Analytics.

## Terminology

A __device__ is a host on the network. A Smart TV or a laptop are examples of devices.

A __device__ is uniquely identified by it's MAC address. Note that MAC randomization has become popular with various devices to enhance privacy. MAC address randomization is an effective way to maintain privacy in public settings, where you don’t know who is looking at your connectivity and location history. But it does create challenges for managing your own network. It is recommended to turn off this feature when connecting to your own managed network, but by all means use the feature when joining public WiFi.

There are 3 primary states for __device__. The states are __registered__, __active__ and __reserved__ and are described below. Note that these states are NOT mutually exclusive. For example, a __device__ could be __registered__ and __active__ but not __reserved__. Therefore, the total number of possible states a __device__ could be in is 7 (2 ^ 3 - 1). 

A __device__ can be __registered__ by you. Registered devices are configured in a simple YAML text file. You may classify similar devices under a group - whatever makes sense for your network. Registered devices may be unclassified - you can manually classify these later. 

A __device__ can be __active__ on the network. This means it has a current DHCP lease and therefore has an IP address.

A __device__ can be __reserved__ where it has a fixed IP reservation. This means it is granted the same static IP address each time it joins the network. 

## How to register devices

To register a device, you will need to capture the MAC address, provide a name for the device and classify it under a grouping. This is to be stored in a file called devices.yml in the current directory, although eventually I will make it more configurable. The devices.yml has to be valid [YAML](https://yaml.org).

An example is provided below:
```
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

# Supports

1. Cisco Meraki powered networks only (for now)
2. IPv4 only (for now)
