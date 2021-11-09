#!/usr/bin/env python3

""" Example of announcing a service (in this case, a fake HTTP server) """

import argparse
import logging
import socket
from time import sleep

from zeroconf import IPVersion, ServiceInfo, Zeroconf

def register_base_service(zeroconf, type_, name, desc, server):

    full_name = "%s.%s" % (name, type_)

    info = ServiceInfo(
        type_,
        full_name,
        addresses=[socket.inet_aton("127.0.0.1")],
        port=80,
        properties=desc,
        server=server
    )
    print("Registration of base service {}".format(type_))

    zeroconf.register_service(info)

def register_subtype(zeroconf, subtype, type, name, desc, server):

    full_subtype = "%s.%s" % (subtype, type)
    full_name = "%s.%s" % (name, type)
    info = zeroconf.get_service_info(type, full_name)
    info.addsubtype(subtype)

    print(f"Registration of subtype service {subtype}")
    zeroconf.update_service(info)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
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

    # First test device
    RTsubtype_ = "_RToic.d.light._sub"
    DIsubtype_ = "_DI54321CA5-4101-4AE4-595B-353C51AA983C._sub"
    type_ = "_ocfd._udp.local."
    name = "54321CA5-4101-4AE4-595B-353C51AA983C"

    desc = {"di": "54321CA5-4101-4AE4-595B-353C51AA983C",
            "rt": "oic.d.light"}

    server="dummy-1.local"
    zeroconf = Zeroconf(ip_version=ip_version)

    register_base_service(zeroconf, type_, name, desc, server)
    register_subtype(zeroconf, DIsubtype_, type_, name, desc, server)
    register_subtype(zeroconf, RTsubtype_, type_, name, desc, server)

    # Second test device
    RTsubtype_ = "_RToic.d.battery._sub"
    DIsubtype_ = "_DI12345CA5-4101-4AE4-595B-353C51AA983C._sub"
    type_ = "_ocfd._udp.local."
    name = "12345CA5-4101-4AE4-595B-353C51AA983C"

    desc = {"di": "12345CA5-4101-4AE4-595B-353C51AA983C",
            "rt": "oic.d.battery"}

    server="dummy-2.local"
    zeroconf = Zeroconf(ip_version=ip_version)

    register_base_service(zeroconf, type_, name, desc, server)
    register_subtype(zeroconf, DIsubtype_, type_, name, desc, server)
    register_subtype(zeroconf, RTsubtype_, type_, name, desc, server)

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_all_services()
        zeroconf.close()
