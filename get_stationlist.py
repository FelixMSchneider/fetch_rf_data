from __future__ import print_function

#
#  get-rf-data is a package to download teleseismic events for
#  Receiver function processing
#
#  author: felix.m.schneider@gmx.de
#
#  USAGE is explaned in the header of fetch_parameter.py
#
#
import sys,os

try:
    from obspy.clients.fdsn.client import Client
    from obspy import UTCDateTime
except:
    print("obspy has to be installed")
    import sys
    sys.exit()

from fetch_parameter import *

if not 'DATAPATH' in locals():
    DATAPATH="./"
DATAPATH=DATAPATH+"/"+network

t1=UTCDateTime(t1_str)
t2=UTCDateTime(t2_str)


if use_routing_client:

    from obspy.clients.fdsn import RoutingClient
    from obspy.clients.fdsn.header import FDSNNoDataException
    client = RoutingClient("eida-routing", credentials={'EIDA_TOKEN': EIDATOKENPATH})
    import warnings
    warnings.filterwarnings('error')
    warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)


    try:
        inventory=client.get_stations(network=network, station="*", starttime=t1, endtime=t2)
    except FDSNNoDataException:
        warnings.filterwarnings("default")
        print("")
        print("   No Data available.")
        print("   Check Input variables")
        print("   station: ", station )
        print("   network: ", network) 
        print("   t1: ", str(t1))
        print("   t2: ", str(t2))
        print("")
        sys.exit()
        
    except Exception as e:

        #warnings.filterwarnings("ignore")

        if "Error 400" in e.args[0]:
            print("")
            print("   EIDA-token " + EIDATOKENPATH + " not valid!")
            print("")
            sys.exit()
        if "EIDA token does not seem to be a valid PGP message" in e.args[0]:
            print("")
            print("   eidatoken not found")
            print("   please check if the eidatoken file exists: ", EIDATOKENPATH)
            print("")
            sys.exit()
        else:
            print(e) 
            pass
    
    warnings.filterwarnings("default")
 

else:
    print("")
    print("search for stations in network "+ network +" in dataclient: " + dataclient)
    print("")

    client = Client(dataclient)
    inventory=client.get_stations(network=network, station="*", starttime=t1, endtime=t2)


os.system("mkdir -p "+ DATAPATH)

f=open(DATAPATH+"/stationlist_"+network+".txt", "w")

statlist=sorted([stat.code for net in inventory.networks for stat in net])

for stat in statlist:
    print(stat, file=f)

f.close()
