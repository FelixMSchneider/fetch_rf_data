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

from get_catalogue_functions import *
import sys,os, os.path

SRCPATH=os.path.dirname(os.path.realpath(__file__))


try:
    from fetch_parameter import DATAPATH
    os.system("mkdir -p "+DATAPATH)
except:
    DATAPATH=SRCPATH

from fetch_parameter import network
DATAPATH=os.path.abspath(DATAPATH+"/"+network)


if len(sys.argv)<2:
    print("")
    print("    usage:") 
    print("    python generate_catalogue.py [station_code]")
    print("")
    print("    or: ")
    print("    python generate_catalogue.py [clat clon]")
    print("    where clat, clon are the reference coordinates used for distance measures")
    print("")
    print("    or:")
    print("    python generate_catalogue.py stationlist.txt")
    print("    to generate individual catalogues for each station in stationlist.txt")
    print("")
    sys.exit()

usestation=False
manystations=False

if len(sys.argv) == 2:
    usestation=True
    station=sys.argv[1]
    from fetch_parameter import network

    if station=="stationlist.txt":
        manystations=True
        slist=DATAPATH+"/stationlist_"+network+".txt"
        import os.path

        slist=os.path.abspath(slist)

        if not os.path.isfile(slist):
            print("") 
            print("    file ", slist ," not found") 
            print("    first run: ")
            print("    python get_stationlist.py")
            print("    to generate the stationlist file")
            print("")
            sys.exit()
          
        print("")
        print("generate individual catalogues for all stations in ", slist)
        print("")

        f=open(slist,"r")

        stations=f.readlines()
        stations=[stat.split()[0] for stat in stations if len(stat.split()) > 0 ]
    else:
        stations=[station]    

if len(sys.argv) == 3:
    slat=float(sys.argv[1])
    slon=float(sys.argv[2])
    stations=["dummy"]



gcat=load_global_cat()

for station in stations:
    if usestation:
        slat,slon=get_station_lat_lon(station)
        print("use station coordinates of station "+station+" as reference")

    if manystations:
        from fetch_parameter import network
        import os
        directory=DATAPATH+"/"+network+"."+station
        os.system("mkdir -p " + directory)
        outfolder=directory
    else:
        outfolder=DATAPATH+"/"


    print("clat, clon = ", slat, slon)

    os.system("mkdir -p "+ outfolder)
    get_catalogue(slat, slon,  outfolder=outfolder, gcat=gcat)
    
