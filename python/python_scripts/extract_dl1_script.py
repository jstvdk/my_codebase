#!/usr/bin/env python3
import h5py
import hdf5plugin
import glob
import numpy as np

filename_event_ids = '/fefs/aswg/workspace/vadym.voitsekhovskyi/2024muons/lst_study/real_data/17043/17043_muons_08complet.txt.npy'
event_ids = np.load(filename_event_ids)


file_path = glob.glob('/fefs/aswg/data/real/DL1/20240310/v0.10/tailcut84/dl1_LST-1.Run17043.*.h5')

# Open the .h5 file
for filename in file_path:
    with h5py.File(filename, 'r') as f:
        # Access the dataset
        dataset = f['dl1/event/telescope/image/LST_LSTCam']
        
        # Read the data
        data = dataset[:]
        
        for event_record in data:
            if event_record[1] in event_ids:
                filename_image = f'/fefs/aswg/workspace/vadym.voitsekhovskyi/2024muons/lst_study/real_data/17043/dl1_image_event{event_record[1]}.txt'
                filename_peak_time = f'/fefs/aswg/workspace/vadym.voitsekhovskyi/2024muons/lst_study/real_data/17043/dl1__peak_time_event{event_record[1]}.txt'
                filename_image_mask = f'/fefs/aswg/workspace/vadym.voitsekhovskyi/2024muons/lst_study/real_data/17043/dl1__image_mask_event{event_record[1]}.txt'
                np.save(filename_image, event_record[2])
                np.save(filename_image_mask, event_record[4])
                np.save(filename_peak_time, event_record[3])
