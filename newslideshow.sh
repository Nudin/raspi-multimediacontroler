#!/bin/bash

convert_image() {
### convert file resolution
   # Note: Convert has different resizing techniques
   # best:        -rescale
   # in between:  -scale
   # fast:        -sample
   convert -sample $2 -gravity center -background black -extent $2 "$1" - | \
   stream -map bgra -extract $2 -virtual-pixel black -storage-type char jpg:- /dev/shm/pic.dat 
}
show_image() {
	cp /dev/shm/pic.dat /dev/fb0
}
IFS='
'

if [ $# -ne 2 ] ; then
	echo "Wrong usage of $0" 1>&2
	exit
fi

timetosleep=$1
# Get the resolution of the framebuffer
resolution=$(fbset -s -fb /dev/fb0 | grep ^mode | cut -d\" -f2)
echo $resolution

if [ -d "$2" ] ; then
	cd "$2"
elif [ -f "$2" ]; then
	# singleimage function
	convert_image "$2" "$resolution"
	show_image
	sleep infinity
else
	echo "Wrong usage of $0" 1>&2
	exit
fi


first=1
for file in *jpg *JPG *jpeg *JPEG; do
   convert_image "$file" "$resolution" &

   if [[ $first -eq 1 ]] ; then
     first=0
   else
     sleep $timetosleep
   fi
   
   while jobs -rp | grep -q ''; do
     sleep 0.1
   done
   
   show_image
done


