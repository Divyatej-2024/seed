from seedemu import *
import os, sys

def run(dumpfile=None, hosts_per_as=2):

    platform = Platform.AMD64  # default

    if dumpfile is None:
        script_name = os.path.basename(__file__)
        if len(sys.argv) == 2:
            if sys.argv[1].lower() == 'arm':
                platform = Platform.ARM64
            elif sys.argv[1].lower() != 'amd':
                print(f"Usage: {script_name} amd|arm")
                sys.exit(1)

    emu     = Emulator()
    base    = Base()
    routing = Routing()
    ebgp    = Ebgp()
    ibgp    = Ibgp()
    ospf    = Ospf()
    web     = WebService()

    # Internet Exchanges
    ix100 = base.createInternetExchange(100)
    ix101 = base.createInternetExchange(101)
    ix102 = base.createInternetExchange(102)

    ix100.getPeeringLan().setDisplayName('Advanced-Practice-100')
    ix101.getPeeringLan().setDisplayName('Advanced-Practice-101')
    ix102.getPeeringLan().setDisplayName('Advanced-Practice-102')

    # Transit AS
    Makers.makeTransitAs(base, 2, [100, 101, 102],
        [(100, 101), (101, 102), (100, 102)]
    )

    Makers.makeTransitAs(base, 3, [100, 101, 102],
        [(100, 101), (101, 102), (100, 102)]
    )

    # Real-world router
    as99999 = base.createAutonomousSystem(99999)
    as99999.createRealWorldRouter(
        'rw-real-world',
        prefixes=['0.0.0.0/1', '128.0.0.0/1']
    ).joinNetwork(ix100.getPeeringLan().getName(), '10.100.0.99')

    # Layers
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
