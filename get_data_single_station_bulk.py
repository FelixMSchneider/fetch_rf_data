from __future__ import print_function

#
#  get-rf-data is a package to download teleseismic events for
#  Receiver function processing
#
#  author: felix.m.schneider@gmx.de
#
#  Data are stored in Q-File format which enables further 
#  procossing with seismic handler
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

import sys
import os, os.path

#########################################################
# read fetch parameter from fetch_parameter.py

from fetch_parameter import *

if not 'DATAPATH' in locals():
    DATAPATH="./"
DATAPATH=DATAPATH+network


t1=UTCDateTime(t1_str)
t2=UTCDateTime(t2_str)


#########################################################

if len(sys.argv)<2:
    print("")
    print("    usage: python get_data_single_station.py [station_code]")
    print("")
    print("    parameters are read from fetch_parameter.py")
    print("")
    sys.exit()

station=sys.argv[1]

##########################################################


###### search for station in  database ####################

####
#
# if a Eida token has to be passed to access restricted data:
#

if eida_routing:
    print("")
    print("search for network "+ network +" and station "+station+" using RoutingClient with Eidatoken " + EIDATOKENPATH)
    print("")

    from obspy.clients.fdsn import RoutingClient
    client = RoutingClient("eida-routing", credentials={'EIDA_TOKEN': EIDATOKENPATH})

    import warnings
    warnings.filterwarnings('error')
    try:
        inventory=client.get_stations(network=network, station=station, starttime=t1, endtime=t2)
    except:
        print("")
        print("EIDA-token " + EIDATOKENPATH + " not valid or not found")
        print("")
        sys.exit()
    warnings.filterwarnings('default')
else:
    print("")
    print("search for network "+ network +" and station "+station+" in dataclient: " + dataclient)
    print("")

    client = Client(dataclient)

    inventory=client.get_stations(network=network, station=station, starttime=t1, endtime=t2)





net=inventory.networks[0]
stat=net.stations[0]

slat=stat.latitude
slon=stat.longitude

############################################################
import os
directory=DATAPATH+"/"+network+"."+station
os.system("mkdir -p " + directory)

os.system("cp fetch_parameter.py " + directory + "/fetch_parameter.log")


###### generate Event catalogue ############################

try:
    cat=obspy.read_events(directory+"/"+catalogue_file,  format="ZMAP")
    print("load catalogue from ", directory+"/"+catalogue_file)
except:
    try:
        cat=obspy.read_events(DATAPATH+"/"+catalogue_file,  format="ZMAP")
        print("load catalogue from ", DATAPATH+"/"+catalogue_file)
    except:
        print("")        
        print("    neither ",DATAPATH+"/"+catalogue_file)
        print("    nor ", directory+"/"+ catalogue_file, " does exist")
        print("")        
        print("    EITHER ")
        print("        generate the catalogue with the command")
        print("")        
        print("          python generate_catalogue.py [refstation] / ")
        print("          python generate_catalogue.py [clat clon]")
        print("")        
        print("    to generate a single network cataloge using the station coordinates of refstation")
        print("    or clat clon as reference coordinates")
        print("")        
        print("    OR ")
        print("")        
        print("         python generate_catalogue.py stationlist.txt")
        print("")
        print("   to generate individual earthquake catalogues for each station listed in stationlist.txt")
        print("")
        sys.exit()
    
    
catfile=directory+"/"+"teleseismic_events_"+network+"."+station+".txt"
os.system("rm -f "+catfile)


#generate logfile to list all events that could not be fetched
logfile=directory+"/"+network+"."+station+".log"
logout=open(logfile, "a") 
print("", file=logout)

try:
    from datetime import datetime
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
except:
    dt_string = ""

print(" XXX NEW RUN XXX " + dt_string, file=logout) 
print("", file=logout) 


############################################################

if not os.path.isfile(directory+"/"+station+".MSEED"):

    ###### get event data for station ############################
    print("")
    print("create bulk request")
    print("")
    
    bulk=[]
    
    for evno in range(len(cat)):
        ev=cat[evno] 
        o=ev.origins[0] 
        m=ev.magnitudes[0] 
        dist=gps2dist_azimuth(o.latitude,o.longitude,slat,slon)[0]/1000.0
     
        origin=o.time 
        evlat=o.latitude 
        evlon=o.longitude 
    
        try:
            evdep=o.depth/1000.0 
        except:
            print("warning: no depth give in catalogue --> set depth to 10.0 km")
            evdep=10.0 # if o.depth is None set evdep to 10 km
        if evdep < 0 : evdep=0.0
    
        dist,az,baz=gps2dist_azimuth(o.latitude,o.longitude,slat,slon) 
        distdeg=dist/(1000.0*111.12 )
     
        model = TauPyModel(model="iasp91") 
     
        phaselist=[phase] 
    
        arrivals = model.get_travel_times(source_depth_in_km=evdep, 
                                          distance_in_degree=distdeg, phase_list=phaselist) 
    
        if len(arrivals)==0: 
            print("no "+phase+"-phase available for event No.", evno)
            continue
     
        inc=arrivals[0].incident_angle
        slowness = arrivals[0].ray_param_sec_degree
        traveltime=arrivals[0].time
        arrivaltime=origin+traveltime
    
        start=arrivaltime-time_before_onset
        stop=arrivaltime+time_after_onset
    
        start=UTCDateTime(round(start.timestamp))
        stop=UTCDateTime(round(stop.timestamp))
    
    
        bulk.append((network, station, "*", "?H?", start,stop))
    
    
    print("")
    print("Check inventory for available channels for station "+ station)
    print("")


    inv=client.get_stations_bulk(bulk, level="channel")
    print(inv)
    
    HH_channels=[channel for channel in [chan.split(".")[-1] for chan in inv.get_contents()["channels"]] if "HH" in channel]
    BH_channels=[channel for channel in [chan.split(".")[-1] for chan in inv.get_contents()["channels"]] if "BH" in channel]
    
    
    print("")
    
    if len(BH_channels)>= 3: 
        print("    BH channel is available --> request BH channels" )
        request_channel="BH"
    elif len(HH_channels)>=3: 
        print("    BH channel is not available but HH is available--> request HH channels" )
        request_channel="HH"
    else:
        print("    no HH or BH channels available for station "+ station)
        sys.exit()
    
    print("")
    print("send bulk request to Client")
    print("")
    
    bulk=[(bulk[i][0], bulk[i][1], bulk[i][2], request_channel+"?", bulk[i][4], bulk[i][5]) for i in range(len(bulk))]
    

    if not eida_routing:
        try: 
            st=client.get_waveforms_bulk(bulk, attach_response=remove_response)
        except obspy.clients.fdsn.header.FDSNNoDataException:
            print("No data available for this request!")
            sys.exit()
    else:
        try:
            st=client.get_waveforms_bulk(bulk)
        except ValueError:
            print("EIDA token not present or valid?")
            sys.exit()
        except obspy.clients.fdsn.header.FDSNNoDataException:
            print("No data available for this request!")
            sys.exit()
        if remove_response:
            print("warning: attachment of instrument response is not supported by RoutingClient")
            print("set remove_reponse to False")
            remove_response=False
    
    st.write(directory+"/"+station+".MSEED", format="MSEED")
else:
    st=obspy.read(directory+"/"+station+".MSEED")
        

print("")
print("now sort all events, set header values, and write into Qfile")
print("")


RFst=obspy.Stream()
model = TauPyModel(model="iasp91") 

for evno in range(len(cat)):
    
    ev=cat[evno]
    o=ev.origins[0]
    m=ev.magnitudes[0]
    dist=gps2dist_azimuth(o.latitude,o.longitude,slat,slon)[0]/1000.0

    origin=o.time
    evlat=o.latitude
    evlon=o.longitude

    try:
        writedep_header=True
        evdep=o.depth/1000.0
    except:
        print("warning: no depth give in catalogue --> set depth to 10.0 km")
        writedep_header=False
        evdep=10.0 # if o.depth is None set evdep to 10 km
    if evdep < 0 : evdep=0.0

    dist,az,baz=gps2dist_azimuth(o.latitude,o.longitude,slat,slon)
    distdeg=dist/(1000.0*111.12 )

    print("event "+ str(evno+1) +" of "+str(len(cat))+": ", o.time, o.latitude,o.longitude, o.depth, round(dist/111.12,2), m.mag)

    phaselist=[phase]
    arrivals = model.get_travel_times(source_depth_in_km=evdep,
                                      distance_in_degree=distdeg, phase_list=phaselist)
    if len(arrivals)==0:
        print("no "+phase+"-phase available for event No.", evno)
        continue

    inc=arrivals[0].incident_angle
    slowness = arrivals[0].ray_param_sec_degree
    traveltime=arrivals[0].time
    arrivaltime=origin+traveltime

    start=arrivaltime-time_before_onset
    stop=arrivaltime+time_after_onset

    start=UTCDateTime(round(start.timestamp))
    stop=UTCDateTime(round(stop.timestamp))


######################################################
# first attempt to assemble ZNE traces from one event
# (quite slow)
#    sti=st.copy()
#    sti.trim(start,stop)
######################################################
# this version is faster (first select only events that
# have reasonable starttimes:
 
    sti=obspy.Stream()
    for tr in st:
        if tr.stats.starttime > start-20 and tr.stats.starttime < stop+20:
            sti+=tr
    
    sti.trim(start,stop)
######################################################
    try:
        sti.merge(fill_value=0)
    except:
        print("warning: merge not possible ---> skip event", evno, network, station, channel+"?", start,stop, file=logout)
        print("warning: merge not possible ---> skip event", evno)
      
        continue

    if len(sti) < 3 : 
        print("no 3 component data for event", evno)
        continue
 


    try:
        # set Header values for seismic handler
        for tr in sti:
             tr.stats.sh=AttribDict()               
             tr.stats.sh.INCI=inc
             tr.stats.sh[phase+"-ONSET"]=arrivaltime
             tr.stats.sh.LAT=evlat
             tr.stats.sh.LON=evlon
             if writedep_header: tr.stats.sh.DEPTH=evdep
             tr.stats.sh.AZIMUTH=baz
             tr.stats.sh.SLOWNESS=slowness
             tr.stats.sh.MAGNITUDE=m.mag
             tr.stats.sh.ORIGIN=o.time
             tr.stats.sh.DISTANCE=distdeg
             tr.stats.sh.DCVREG=slat    
             tr.stats.sh.DCVINCI=slon
    
        # remove instrument response
        if remove_response:
            sti.remove_response(output="VEL")

        sti.detrend()
        sti.detrend(type="demean")
        
        channels=[] 
        #add event data to Stream
        tr=sti.select(component="z")[0]
        RFst+=tr
        #print("add channel", tr.stats.channel)
        channels.append(tr.stats.channel)

 
        # ZNE
        tr=sti.select(component="n")

        if len(tr)==1:
            tr=tr[0]
            RFst += tr
            channels.append(tr.stats.channel)

            tr=sti.select(component="e")[0]
            RFst += tr
            channels.append(tr.stats.channel)

        # Z12
        else:
            tr=sti.select(component="1")
            if len(tr)==1:
                tr=tr[0]
                RFst += tr
                channels.append(tr.stats.channel)

                tr=sti.select(component="2")[0]
                RFst += tr
                channels.append(tr.stats.channel)

         # Z23
            else:
                tr=sti.select(component="2")
                if len(tr)==1:
                    tr=tr[0]
                    RFst += tr
                    channels.append(tr.stats.channel)

                    tr=sti.select(component="3")[0]
                    RFst += tr
                    channels.append(tr.stats.channel)

        catout=open(catfile, "a")
        print("%3d %28s %8.3f %8.3f %7.2f %5.2f %3.1f %3s %3s %3s" % (evno, o.time, o.latitude,o.longitude, evdep, round(dist/111.12,2), m.mag, channels[0], channels[1], channels[2]), file=catout)
        catout.close()

    except:
        print("some conversion error for event ",evno, network, station, channel+"?", start,stop, file=logout) 
        print("some conversion error for event ",evno, network, station, channel+"?", start,stop) 
        continue



# write QFILE which should be readable with seismic handler
RFst.write(directory+"/QFILE.QHD", format="Q", append=True)

#################################################################################
# correct header-file which is corrupted due to bug in obspy io.sh append function
sth=obspy.read(directory+"/QFILE.QHD", headonly=True)
sth.write(directory+"/XXX.QHD", format="Q")
os.system("mv " + directory+"/XXX.QHD " + directory + "/QFILE.QHD") 
os.system("rm " + directory+ "/XXX.QBN")
################################################################################# 
logout.close()