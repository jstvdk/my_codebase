#!/bin/bash

cd /Users/vdk/Software/my_code/python/sofi/data/rad_photo_custom/imgs

for i in {1..54}; do
    # Construct the source and destination filenames
    src="with_label_${i}.jpg"
    dest="sign_${i}.jpg"
    
    # Copy the file with the new name
    cp "$src" "$dest"
done
