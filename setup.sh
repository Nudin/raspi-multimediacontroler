#!/bin/bash

resolution=$(fbset -s -fb /dev/fb0 | grep ^mode | cut -d\" -f2)

   # Note: Convert has different resizing techniques
   # best:        -rescale
   # in between:  -scale
   # fast:        -sample
convert -sample $resolution -gravity center -background black -extent $resolution clear.jpg - | \
stream -map bgra -extract $resolution -virtual-pixel black -storage-type char jpg:- clear.dat &
