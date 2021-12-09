
try:
    import obspy
    from obspy.core import AttribDict
    from obspy.taup import TauPyModel

    from obspy.clients.fdsn.client import Client
    from obspy import UTCDateTime
    from obspy.geodetics import gps2dist_azimuth
except:
    print("obspy has to be installed")
    import sys
    sys.exit()

import sys
from fetch_parameter import *


client = Client(dataclient)

inv=client.get_stations(network=network, level="channel")

idlist=[]

for id in inv[0].get_contents()["channels"]:
    idlist.append(id)

idlist=sorted(list(set(idlist)))


outfile=open("station_list_"+network+".dat", "w")

prev_station="dummy"
for id in idlist:

    station=id.split(".")[1]
    channel=id.split(".")[-1]

    if station != prev_station:
        statdict=inv.get_coordinates(id)
        latitude=statdict["latitude"]
        longitude=statdict["longitude"]
        elevation=statdict["elevation"]

        if prev_station != "dummy": print("", file=outfile)

        print("%7s %7.3f %7.3f %6.1f" % (station, latitude,longitude,elevation),  end='', file=outfile)

    print(" %3s" %  (channel),  end='', file=outfile)

    prev_station=station

print("", file=outfile)
print("")

