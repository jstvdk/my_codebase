import sys
import numpy as np
import pandas as pd
import csv
import scipy
import matplotlib.pyplot as plt
from seaborn import histplot
import random
import copy
from os import path, makedirs
from astropy.coordinates import SkyCoord
from astropy.table import Table
import astropy.units as u
from ctapipe.containers import MuonEfficiencyContainer
from ctapipe.coordinates import CameraFrame, TelescopeFrame
from ctapipe.io import EventSource, EventSeeker
from ctapipe.core import TelescopeComponent
from ctapipe.core.traits import (
    List,
    Int,
    FloatTelescopeParameter,
    TelescopeParameter,
    Unicode,
)
from ctapipe.image.cleaning import tailcuts_clean
from ctapipe.image.muon import MuonRingFitter, MuonIntensityFitter
from traitlets.config import Config
from ctapipe.image import ImageProcessor
from ctapipe.image.muon import MuonProcessor
from ctapipe.visualization import CameraDisplay
from ctapipe.instrument import CameraGeometry
from ctapipe.calib import CameraCalibrator
from traitlets.config.loader import Config, FileConfigLoader, JSONFileConfigLoader
import pathlib
from traitlets.config import Config
from astropy.time import Time
from astropy.coordinates import EarthLocation,SkyCoord, AltAz 
from traitlets.config import Config
import time
from ctapipe.image import number_of_islands


# TIME_CLEANING + ISLAND_CLEANING + FLAGGING



start = int(sys.argv[1])
stop = int(sys.argv[2])

print(f"start = {sys.argv[1]}")
print(f"stop = {sys.argv[2]}")


min_pixel = 30
checker = 0
r1_cut = 2
min_pixel_cut = 60
max_pixel_cut = 200
low_threshold_variance = 0.1
up_threshold_variance = 0.4
max_time = 14


muon_processor_config_2 = Config({"MuonProcessor":
                                {"ImageParameterQuery" :
                                 {"quality_criteria" : [["min_pixels", f"dl1_params.morphology.n_pixels > {min_pixel}"],
                                                        ["min_intensity", "dl1_params.hillas.intensity > 500"]]}}})
t1 = time.perf_counter(), time.process_time()

for run in range(start,stop):
    #filename = f'/Users/vdk/LST/LST_work/corsika_4LSTprotons/simtel_corsika_run{run}.simtel.gz'
    filename = f'/fefs/aswg/mc/LST_Advanced_Camera_Prod1/proton/zenith_20deg/south_pointing/4LSTs_PMT/sim_telarray/simtel_corsika_run{run}.simtel.gz'
    source = EventSource(filename)
    event_iterator = iter(source)
    optical_efficiency_list = []
    for i,event in enumerate(event_iterator):
        
        image_processor = ImageProcessor(source.subarray)
        muon_processor = MuonProcessor(source.subarray, config = muon_processor_config_2)
        calib = CameraCalibrator(image_extractor_type="GlobalPeakWindowSum",subarray = source.subarray)

        if len(event.trigger.tels_with_trigger) > 1:
            for tels in event.trigger.tels_with_trigger:

                tmp_arr = []
                var_arr = []
                for pix_id in event.r1.tel[tels].waveform[:,10:max_time]:
                    tmp_arr.append(np.max(pix_id)) # знаходить максимальне значення waveform в кожному пікселі
                    var_arr.append(np.var(pix_id))
            
            tmp_arr = np.array(tmp_arr)
            pixel_number = len(tmp_arr[tmp_arr>r1_cut])
            
            if (pixel_number > min_pixel_cut) and (pixel_number < max_pixel_cut) and (np.mean(var_arr) >low_threshold_variance) and (np.mean(var_arr) < up_threshold_variance):
                pixel_mask = []
                original_r1_waveform = event.r1.tel[tels].waveform.copy()
                for_clean_mask = []

                for k,l in enumerate(event.r0.tel[tels].waveform[1]):
                    if np.argmax(l) in range(17,41): 
                        pixel_mask.append(True)
                    else:
                        pixel_mask.append(False)

                working_wave = event.r1.tel[tels].waveform.copy()
                for k,l in enumerate(working_wave):
                    if pixel_mask[k]:
                        for_clean_mask.append(True)
                        #working_wave[k] = np.zeros(40)     
                        working_wave[k] = np.mean(event.r1.tel[tels].waveform, axis = 0)
                    else:
                        for_clean_mask.append(False)
                event.r1.tel[tels].waveform = working_wave

                calib(event)
                image_processor(event)
                cam_geometry = source.subarray.tel[tels].camera.geometry
                return_pixels = np.array([])
                for_clean_mask = np.array(for_clean_mask)
                n_islands, island_id = number_of_islands(cam_geometry, for_clean_mask)

                for t in range(1,n_islands+1):
                    if len(np.where(island_id == t)[0]) <= 3:
                        return_pixels = np.append(return_pixels,np.where(island_id ==t)[0])

                return_pixels = return_pixels.astype(int)

                event.r1.tel[tels].waveform[return_pixels,:] = original_r1_waveform[return_pixels,:]  

                calib(event)
                image_processor(event)
                muon_processor(event)   
                    
                if len(event.muon.tel.keys()):       
                    for tels in event.muon.tel.keys():
                        if not np.isnan(event.muon.tel[tels].efficiency.width):
                           if (event.dl1.tel[tels].parameters.morphology.n_pixels > 50 and abs(event.muon.tel[tels].parameters.intensity_ratio - 1) < 0.3 and event.muon.tel[tels].parameters.completeness > 0.5 and event.muon.tel[tels].parameters.mean_squared_error.to_value() < 0.01):
                               optical_efficiency_list.append(event.muon.tel[tels].efficiency.optical_efficiency) 
    
    result = ','.join(map(str, optical_efficiency_list))
    with open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/opt_eff_{start}_{stop}.txt", 'a') as fout:
        if result:
            fout.write(result)
            fout.write(',')
    with open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/opt_eff_runStat_{start}_{stop}.txt", 'a') as fout:
        fout.write(f"run {run} = {len(optical_efficiency_list)} \n")

    t2 = time.perf_counter(), time.process_time()   

    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")








