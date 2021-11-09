#!/usr/bin/env python3

""" Example of browsing for a service.

The default is HTTP and HAP; use --find to search for all available services in the network
"""

import argparse
import logging
from time import sleep
from typing import cast

from zeroconf import IPVersion, ServiceBrowser, ServiceStateChange, Zeroconf, ZeroconfServiceTypes


def on_service_state_change(
    zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
) -> None:
    print(f"Service {name} of type {service_type} state changed: {state_change}")

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        print("Info from zeroconf.get_service_info: %r" % (info))

        if info:
            addresses = ["%s:%d" % (addr, cast(int, info.port)) for addr in info.parsed_scoped_addresses()]
            print("PTR Record(s):")
            print(f"  Type: {info.type} Instance Name: {info.dns_pointer().alias}")
            subtype_ptrs = info.dns_pointer_subtypes()
            if subtype_ptrs:
                for subtype_ptr in subtype_ptrs:
                    print(f"   Type: {subtype_ptr.type}  Instance Name: {subtype_ptr.alias}")
            print("SRV Record:")
            print(f"  Name: {info.name}")
            print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            print(f"  Server: {info.server}")
            print("TXT Record:")
            print(f"  Name{info.name}")
            if info.properties:
                print("  Properties are:")
                for key, value in info.properties.items():
                    print(f"    {key}: {value}")
            else:
                print("  No properties")

            print("AAAA Record:")
            print(f"  Server: {info.server}")
            print("  Addresses: %s" % ", ".join(addresses))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--find', action='store_true', help='Browse all available services')
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--v6', action='store_true')
    version_group.add_argument('--v6-only', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only

    zeroconf = Zeroconf(ip_version=ip_version)

    services = ["_RToic.d.battery._sub._ocfd._udp.local."]
    if args.find:
        services = list(ZeroconfServiceTypes.find(zc=zeroconf))

    print("\nBrowsing %d service(s), press Ctrl-C to exit...\n" % len(services))
    browser = ServiceBrowser(zeroconf, services, handlers=[on_service_state_change])

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
