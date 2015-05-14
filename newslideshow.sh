#!/bin/bash

timetosleep=$1
cd "$2"

resolution=$(fbset -s -fb /dev/fb0 | grep ^mode | cut -d\" -f2)

first=1
for i in *jpg *JPG *jpeg *JPEG; do
   # Note: Convert has different resizing techniques
   # best:        -rescale
   # in between:  -scale
   # fast:        -sample
   convert -sample $resolution -gravity center -background black -extent $resolution "$i" - | \
   stream -map bgra -extract $resolution -virtual-pixel black -storage-type char jpg:- /dev/shm/pic.dat &
   
   if [[ $first -eq 1 ]] ; then
     first=0
   else
     sleep $timetosleep
   fi
   
   while jobs -rp | grep -q ''; do
     sleep 0.1
   done
   
   cp /dev/shm/pic.dat /dev/fb0
done


