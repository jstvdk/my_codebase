#!/bin/bash

DIRECTORY="/Users/vdk/Software/ctasoft/aiv_integration/test-report"

for FILE in "$DIRECTORY"/*
do
   if [ -f "$FILE" ]; then
      grep -sH ".*operation_call*." "$FILE"
   fi
done


