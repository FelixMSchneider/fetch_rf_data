###################################################################
#
#  get-rf-data is a package to download teleseismic events for
#  Receiver function processing
#
#  author: felix.m.schneider@gmx.de
#
#  Data are stored in Q-File format which enables further 
#  processing with seismic handler
###################################################################

#
# fetch_parameter.py: Parameter file to control data download
# with get_data_single_station.py / get_data_many_stations.sh
#
# usage: see: USAGE.txt


network="Z3"

DATAPATH="/home/felix/RFdata_V3/"

use_routing_client=False

pass_eidatoken=True
EIDATOKENPATH="/home/felix/eidatoken_RK3"

# [t1_str,t2_str]: time intervall of event request
# format: "YYYY-MM-DD"
t1_str="2015-01-01"   
t2_str="2020-04-01"

#phase="P"
phase="S"

time_before_onset = 300
time_after_onset  = 300

minradius=55
maxradius=85

minmagnitude=6.5
maxmagnitude=10


# remove_response option is not possible for use_routing_client=True ()
remove_response=False
#remove_response=True

# dataclient is used to request data (only relevant if use_routing_client=False
#dataclient="LMU"
dataclient="ORFEUS"
#dataclient="http://erde.geophysik.uni-muenchen.de"
#dataclient="http://webservices.ingv.it"

# other possible dataclients:
#
# BGR         http://eida.bgr.de
# EMSC        http://www.seismicportal.eu
# ETH         http://eida.ethz.ch
# GEONET      http://service.geonet.org.nz
# GFZ         http://geofon.gfz-potsdam.de
# ICGC        http://ws.icgc.cat
# INGV        http://webservices.ingv.it
# IPGP        http://ws.ipgp.fr
# IRIS        http://service.iris.edu
# ISC         http://isc-mirror.iris.washington.edu
# KNMI        http://rdsa.knmi.nl
# KOERI       http://eida.koeri.boun.edu.tr
# LMU         http://erde.geophysik.uni-muenchen.de
# NCEDC       http://service.ncedc.org
# NIEP        http://eida-sc3.infp.ro
# NOA         http://eida.gein.noa.gr
# ODC         http://www.orfeus-eu.org
# ORFEUS      http://www.orfeus-eu.org
# RASPISHAKE  http://fdsnws.raspberryshakedata.com
# RESIF       http://ws.resif.fr
# SCEDC       http://service.scedc.caltech.edu
# TEXNET      http://rtserve.beg.utexas.edu
# USGS        http://earthquake.usgs.gov
# USP         http://sismo.iag.usp.time_before_onset


######################################################
#  II. options on the GLOBALE earthquake catalog 


# this global catalogue has to be generated once with 
#
#  python generate_global_catalogue.py
#
#

global_earthquake_calalogue="GLOBAL_EQ_CAT_1980_112021_MGT55.txt"
global_t1_str="1980-01-01"

# global_t2_str can be either "NOW" or "YYYY-MM-DD"-format
global_t2_str="NOW"

global_minmagnitude=5.5

eventclient="USGS"

# other possible event clients (tested 08/2021) :
# EMSC 
# INGV 
# IRIS 
# ISC  
# NCEDC
# USGS 
 
catalogue_file=phase+"RF-EVENTS.txt"

