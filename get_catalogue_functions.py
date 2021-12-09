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
#
#  either generate the catalogue using a local GLOBAL earthquake catalogue file
#  or generate the catalogue from online service
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

import sys


def get_station_lat_lon(station):
    from fetch_parameter import t1_str,t2_str, dataclient, network, eida_routing, EIDATOKENPATH

    t1=UTCDateTime(t1_str)
    t2=UTCDateTime(t2_str)

    if eida_routing:

        from obspy.clients.fdsn import RoutingClient
        client = RoutingClient("eida-routing", credentials={'EIDA_TOKEN': EIDATOKENPATH})

        import warnings
        warnings.filterwarnings('error')
        try:
            inventory=client.get_stations(network=network, station=station, starttime=t1, endtime=t2)
        except ResourceWarning:
            pass
        except:
            print("")
            print("EIDA-token " + EIDATOKENPATH + " not valid or not found")
            print("")
            sys.exit()
        warnings.filterwarnings('default')

    else:
        client = Client(dataclient)
        inventory=client.get_stations(network=network, station=station, starttime=t1, endtime=t2)

    net=inventory.networks[0]
    stat=net.stations[0]

    slat=stat.latitude
    slon=stat.longitude
    return slat,slon

def load_global_cat():
    from fetch_parameter import global_earthquake_calalogue

    import os
    SRCPATH=os.path.dirname(os.path.realpath(__file__))

    try:
        from fetch_parameter import DATAPATH
        os.system("mkdir -p "+DATAPATH)
    except:
        DATAPATH=SRCPATH

    gcatfname=DATAPATH+"/"+global_earthquake_calalogue

    if not os.path.isfile(gcatfname):
        DATAPATH=SRCPATH
        gcatfname2=DATAPATH+"/"+global_earthquake_calalogue
        if os.path.isfile(gcatfname2):
            print("Warning: file not found "+gcatfname)
            print("use "+ gcatfname2)
            gcatfname=gcatfname2
        else:
            print("Error: file not found "+ gcatfname)
            if gcatfname != gcatfname2:
                print("Error: file not found "+ gcatfname2)
            sys.exit()


    print("load global catalogue from file:")
    print(gcatfname)
    print("... (takes some time)")

    cat = obspy.read_events(gcatfname)
    return cat

def get_catalogue(clat,clon, outfolder=".", returncat=False, gcat=None):
    
    #########################################################
    # read fetch parameter from fetch_parameter.py
    
    from fetch_parameter import t1_str,t2_str, eventclient, minmagnitude,maxmagnitude,minradius,maxradius, catalogue_file,global_earthquake_calalogue

    t1=UTCDateTime(t1_str)
    t2=UTCDateTime(t2_str)
    
    ###### generate Event catalogue ############################
   
    if gcat == None:
        cat = load_global_cat()
    else:
        cat=gcat
    
    print("")
    print("generate catalogue with teleseismic events...")
    print("")
    print("Time range: " + str(t1) +" to "+str(t2))
    print("Distance range: " + str(minradius) +" to "+str(maxradius))
    print("Manitude range: " + str(minmagnitude) +" to "+str(maxmagnitude))
    print("")
    
    
    catt=cat.filter("time > "+str(t1), "time < "+str(t2))
    
    newcat=obspy.core.event.Catalog()
    
    k=0
    for i,ev in enumerate(catt):
    
        lon=ev["origins"][0]["longitude"]
        lat=ev["origins"][0]["latitude"]
        time=ev["origins"][0]["time"]

        dist_deg=obspy.geodetics.gps2dist_azimuth(lat,lon,clat,clon)[0]/1000.0/111.112
        mag=ev["magnitudes"][0]["mag"]

        if dist_deg < maxradius and dist_deg > minradius and mag < maxmagnitude and mag > minmagnitude:

            newcat=newcat+ev
            print("%3d %28s %8.3f %8.3f %5.2f %3.1f" % (k, time, lat, lon, dist_deg, mag))        
            k+=1
    
    print("save catalogue to ", outfolder+"/"+catalogue_file)
    print("this file can be optionally used for following queries")
    newcat.write(outfolder+"/"+ catalogue_file, format="ZMAP")



    if returncat:
        return newcat
        
