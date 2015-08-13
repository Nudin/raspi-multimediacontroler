#!/bin/bash

resolution=$(fbset -s -fb /dev/fb0 | grep ^mode | cut -d\" -f2)
file=/boot/MEDIA/startscreen.jpg
filetype=jpg

convert -resize $resolution -gravity center -background black -extent $resolution $file - | \
stream -map bgra -extract $resolution -virtual-pixel black -storage-type char $filetype:- /dev/shm/clear.dat &
