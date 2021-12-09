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

import sys,os

try:
    from fetch_parameter import DATAPATH
    os.system("mkdir -p "+DATAPATH)
except:
    DATAPATH="./"



from fetch_parameter import global_t1_str,global_minmagnitude,eventclient,global_earthquake_calalogue

t1=UTCDateTime(global_t1_str)

now=UTCDateTime()
if "global_t2_str" in locals():
    if global_t2_str.upper()=="NOW" or global_t2_str=="":
        t2=now
    else:
        t2=UTCDateTime(global_t2_str)
else:
    t2=now


minmagnitude=global_minmagnitude
maxmagnitude=10.0
eventclient=eventclient
catalogue_file=global_earthquake_calalogue

###### generate Event catalogue ############################

client = Client(eventclient)
print("")
print("generate global catalogue with teleseismic events...")
print("")
print("Time range: " + str(t1) +" to "+str(t2))
print("Manitude range: " + str(minmagnitude) +" to "+str(maxmagnitude))
print("")

i=0

it1=t1
it2=it1.replace(year=it1.year+1)
while it1<now:
    print(it1,it2)
    if it2>now:
        it2=now
    try:
        cat = client.get_events(starttime=it1, endtime=it2, minmagnitude=minmagnitude, maxmagnitude=maxmagnitude)
    except:
        print("get events not successful for ", it1, it2)
        continue
    if i==0: global_cat=cat
    else:
        global_cat=global_cat+cat

    it1=it1.replace(year=it1.year+1)
    it2=it2.replace(year=it2.year+1)
    i+=1


print("save catalogue to ", DATAPATH+"/"+catalogue_file)
print("this file can be optionally used for following queries")
global_cat.write(DATAPATH+"/"+catalogue_file, format="ZMAP")



