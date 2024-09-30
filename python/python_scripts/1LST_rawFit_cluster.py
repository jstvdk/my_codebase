import sys
import numpy as np
import pandas as pd
import scipy
import random
import copy
from os import path, makedirs
from astropy.table import Table
import astropy.units as u
from ctapipe.io import EventSource
from ctapipe.image.cleaning import tailcuts_clean
from ctapipe.image.muon import MuonRingFitter, MuonIntensityFitter
from traitlets.config import Config
from ctapipe.image import ImageProcessor
from ctapipe.image.muon import MuonProcessor
from ctapipe.visualization import CameraDisplay
from ctapipe.instrument import CameraGeometry
from ctapipe.calib import CameraCalibrator
import time

from lstchain.io import replace_config, standard_config


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
source_cfg = Config({
    "source_config": {
        "EventSource" : {
            "allowed_tels": [1],"max_events": 10}},
        "PointingSource":{
            "drive_report_path": '/fefs/onsite/monitoring/driveLST1/DrivePositioning/DrivePosition_log_20231007.txt'},
        "LSTR0Corrections": {
          "calib_scale_high_gain":1.088,
          "calib_scale_low_gain":1.004,
          "drs4_pedestal_path": '/fefs/aswg/data/real/monitoring/PixelCalibration/Cat-A/drs4_baseline/20231007/v0.10.2/drs4_pedestal.Run14937.0000.h5',
          "calibration_path": '/fefs/aswg/data/real/monitoring/PixelCalibration/Cat-A/calibration/20231007/v0.10.4/calibration_filters_52.Run14938.0000.h',
          "drs4_time_calibration_path": '/fefs/aswg/data/real/monitoring/PixelCalibration/Cat-A/drs4_time_sampling_from_FF/20220518/v0.10.0/time_calibration.Run08349.0000.h5'
      }})

custom_config = Config({})

t1 = time.perf_counter(), time.process_time()

for run in range(start,stop):
    subrun = eval(str(4-len(str(run))))*'0' + str(run) # string realisation for subran number
    filename = f'/fefs/aswg/data/real/R0/20231007/LST-1.2.Run14954.{subrun}.fits.fz'
    source = EventSource(filename, config = source_cfg)
    event_iterator = iter(source)
    config = replace_config(standard_config, custom_config)
    optical_efficiency_list = []
    event_list = []
    image_processor = ImageProcessor(source.subarray)
    muon_processor = MuonProcessor(source.subarray, config = muon_processor_config)
    calib = CameraCalibrator(image_extractor_type="GlobalPeakWindowSum",subarray = source.subarray, config = Config(config))
    for i,event in enumerate(event_iterator):
        


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
    with open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/output14948/ctapipe/opt_eff_raw_{start}_{stop}.txt", 'a') as fout:
        if result:
            fout.write(result)
            fout.write(',')
    with open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/output14948/ctapipe/opt_eff_raw_runStat_{start}_{stop}.txt", 'a') as fout:
        if result_event:
            fout.write(result_event)
            fout.write(',')

    t2 = time.perf_counter(), time.process_time()  

    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")








