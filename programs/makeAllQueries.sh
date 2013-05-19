#!/bin/bash

DATA=./data
PROGRAMS=${WCODE}/programs
MAKEFILE=Makefile

for FILE in ${DATA}/*.gz
do
    if [ -f $FILE ] ; then
        BASENAME=`basename $FILE`
        RAWDATA=${BASENAME%\.*}
        if [ ! -f ${DATA}/${RAWDATA}.queries ]
        then
            export INDEX=$RAWDATA # kludge to keep Makefile happy
            echo "Unzipping $BASENAME . . . "
            gunzip $FILE
            make -f $MAKEFILE queries
            rm -f ${DATA}/${RAWDATA}.filtered
            echo "Zipping $RAWDATA . . . "
            gzip ${DATA}/${RAWDATA}
        fi
    fi 
done
