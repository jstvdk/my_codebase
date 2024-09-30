#!/usr/bin/env python3
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


int_cut = 0.3
checker = 0
r1_cut = 2
min_pixel_cut = 60
max_pixel_cut = 200
low_threshold_variance = 0.1
up_threshold_variance = 0.4
max_time = 14


muon_processor_config = Config({"MuonProcessor": 
                                {"RingQuery": 
                                 {"quality_criteria" : [["intensity_check",f"np.abs(parameters.intensity_ratio - 1) < {int_cut}"],
                                                        ["ring_containment", "parameters.containment > 0.5"],
                                                        ["ring_completeness", "parameters.completeness > 0.5"]]}}})
t1 = time.perf_counter(), time.process_time()

for run in range(start,stop):
    filename = f'/fefs/aswg/mc/LST_Advanced_Camera_Prod1/proton/zenith_20deg/south_pointing/4LSTs_PMT/sim_telarray/simtel_corsika_run{run}.simtel.gz'
    source = EventSource(filename)
    event_iterator = iter(source)
    optical_efficiency_list = []
    event_list = []
    counter = 0
    for i,event in enumerate(event_iterator):
        if len(event.trigger.tels_with_trigger) > 1:
            counter += 1
            image_processor = ImageProcessor(source.subarray)
            muon_processor = MuonProcessor(source.subarray, config = muon_processor_config)
            calib = CameraCalibrator(image_extractor_type="GlobalPeakWindowSum",subarray = source.subarray)

            calib(event)
            image_processor(event)
            muon_processor(event)   
                        
            if len(event.muon.tel.keys()):       
                for tels in event.muon.tel.keys():
                    if not np.isnan(event.muon.tel[tels].efficiency.width):
                        if (event.dl1.tel[tels].parameters.morphology.n_pixels > 50 and event.muon.tel[tels].parameters.completeness > 0.5 and event.muon.tel[tels].parameters.mean_squared_error.to_value() < 0.01):
                            optical_efficiency_list.append(event.muon.tel[tels].efficiency.optical_efficiency)
                        event_list.append(run*1000+i)
    
    result = ','.join(map(str, optical_efficiency_list))
    result_event = ','.join(map(str,event_list))
    with open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/output/opt_eff_raw_stereo_{start}_{stop}.txt", 'a') as fout:
        if result:
            fout.write(result)
            fout.write(',')
    with open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/output/opt_eff_raw_stereo_runStat_{start}_{stop}.txt", 'a') as fout:
        if result_event:
            fout.write(result_event)
            fout.write(',')
    with open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/output/opt_eff_raw_stereo_AllEvents_{start}_{stop}.txt", 'a') as fout:
        fout.write(str(counter))
        fout.write(',')

    t2 = time.perf_counter(), time.process_time()   

    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")








