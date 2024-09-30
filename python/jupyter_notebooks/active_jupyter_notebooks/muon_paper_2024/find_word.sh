#!/bin/bash

DIRECTORY="/Users/vdk/Software/ctasoft/lst-sim-config"

for FILE in "$DIRECTORY"/*
do
   if [ -f "$FILE" ]; then
      grep -sH "ImageExtractor" "$FILE"
   fi
done


