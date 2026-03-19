#!/usr/bin/env python3
# encoding: utf-8

from seedemu import *
import os, sys
POLICY_FILE =  "policies.json"
def run(dumpfile=None, hosts_per_as=2):

    if dumpfile is None:
        script_name = os.path.basename(__file__)
        if len(sys.argv) == 1:
            platform = Platform.AMD64
        elif len(sys.argv) == 2:
            if sys.argv[1].lower() == 'amd':
                platform = Platform.AMD64
            elif sys.argv[1].lower() == 'arm':
                platform = Platform.ARM64
            else:
                print(f"Usage: {script_name} amd|arm")
                sys.exit(1)
        else:
            print(f"Usage: {script_name} amd|arm")
            sys.exit(1)

    emu     = Emulator()
    base    = Base()
    routing = Routing()
    ebgp    = Ebgp()
    ibgp    = Ibgp()
    ospf    = Ospf()
    web     = WebService()

    ###########################################################################
    # 3 Internet Exchanges (3 hubs/stars on the map)
    ###########################################################################
    ix100 = base.createInternetExchange(100)
    ix101 = base.createInternetExchange(101)
    ix102 = base.createInternetExchange(102)

    ix100.getPeeringLan().setDisplayName('Advanced-Practice-100')
    ix101.getPeeringLan().setDisplayName('Advanced-Practice-101')
    ix102.getPeeringLan().setDisplayName('Advanced-Practice-102')

    ###########################################################################
    # Transit ASes — connect all 3 stars to each other
    ###########################################################################
    Makers.makeTransitAs(base, 2, [100, 101, 102],
        [(100, 101), (101, 102), (100, 102)])
  
    Makers.makeTransitAs(base, 3, [100, 101, 102],
        [(100, 101), (101, 102), (100, 102)]
    )

    ###########################################################################
    #
    ###########################################################################
    Makers.makeStubAsWithHosts(emu, base, 150, 100, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 151, 100, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 152, 100, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 153, 100, hosts_per_as)

    ###########################################################################
 
    ###########################################################################
    Makers.makeStubAsWithHosts(emu, base, 160, 101, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 161, 101, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 162, 101, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 163, 101, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 164, 101, hosts_per_as)

    ###########################################################################
    # B
    ###########################################################################
    Makers.makeStubAsWithHosts(emu, base, 170, 102, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 171, 102, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 172, 102, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 173, 102, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 174, 102, hosts_per_as)
    Makers.makeStubAsWithHosts(emu, base, 175, 102, hosts_per_as)

    ###########################################################################
    # Real-world router — enables pinging real internet (8.8.8.8)
    ###########################################################################
    as99999 = base.createAutonomousSystem(99999)
    as99999.createRealWorldRouter(
        'rw-real-world',
        prefixes=['0.0.0.0/1', '128.0.0.0/1']
    ).joinNetwork('ix100', '10.100.0.99')

    ###########################################################################
    # BGP Peering
    ###########################################################################
    ebgp.addRsPeers(100, [2, 3])
    ebgp.addRsPeers(101, [2, 3])
    ebgp.addRsPeers(102, [2, 3])

    # Left star stubs + real-world internet
    ebgp.addPrivatePeerings(100, [2], [150, 151],         PeerRelationship.Provider)
    ebgp.addPrivatePeerings(100, [3], [152, 153, 99999],  PeerRelationship.Provider)

    # Top-right star stubs
    ebgp.addPrivatePeerings(101, [2], [160, 161, 162],    PeerRelationship.Provider)
    ebgp.addPrivatePeerings(101, [3], [163, 164],         PeerRelationship.Provider)

    # Bottom-right star stubs
    ebgp.addPrivatePeerings(102, [2], [170, 171, 172],    PeerRelationship.Provider)
    ebgp.addPrivatePeerings(102, [3], [173, 174, 175],    PeerRelationship.Provider)

    ###########################################################################
    emu.addLayer(base)
    emu.addLayer(routing)
    emu.addLayer(ebgp)
    emu.addLayer(ibgp)
    emu.addLayer(ospf)
    emu.addLayer(web)

    if dumpfile is not None:
        emu.dump(dumpfile)
    else:
        emu.render()
        emu.compile(Docker(platform=platform), './output', override=True)

if __name__ == "__main__":
    run()
