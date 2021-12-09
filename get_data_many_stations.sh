#!/bin/bash


#
#  get-rf-data is a bash/python package to download teleseismic events for
#  Receiver function processing
#
#  author: felix.m.schneider@gmx.de
#
#  USAGE is explaned in the header of fetch_parameter.py
#
#

DATAPATH=`grep DATAPATH fetch_parameter.py |grep -v "^#" |cut -f2 -d"="|sed 's/"//'g`
NETWORK=`grep network fetch_parameter.py |grep -v "^#"|cut -f2 -d"="|sed 's/"//'g`

stationlist=${DATAPATH}/${NETWORK}/stationlist_${NETWORK}.txt



if [ ! -f $stationlist ]
then
echo ""
echo "    FILE NOT FOUND: $stationlist"
echo ""
echo "    please generate stationlist using: python get_stationlist.py"
echo ""
exit
fi

# run N jobs in parallel

N=1


for station in `cat $stationlist`
do
    (
    python get_data_single_station_bulk.py $station
    ) &

    # allow to execute up to $N jobs in parallel
    if [[ $(jobs -r -p | wc -l) -ge $N ]]; then
        # now there are $N jobs already running, so wait here for any job
        # to be finished so there is a place to start next one.
        wait -n
    fi

done

# no more jobs to be started but wait for pending jobs
# (all need to be finished)
wait

echo "all done"
