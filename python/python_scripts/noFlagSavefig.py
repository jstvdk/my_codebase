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



for run in range(start,stop):
    filename = f'/fefs/aswg/mc/LST_Advanced_Camera_Prod1/proton/zenith_20deg/south_pointing/4LSTs_PMT/sim_telarray/simtel_corsika_run{run}.simtel.gz'
    source = EventSource(filename)
    event_iterator = iter(source)
    event_list = []
    for i,event in enumerate(event_iterator):
        if (str(run*1000+i)) in checked_events:
            for tels in event.trigger.tels_with_trigger: 
                plt.figure(figsize = (9,6))
                camgeom = source.subarray.tel[tels].camera.geometry
                title=f"event_{run*1000+i}"
                disp = CameraDisplay(camgeom,title=title)
                disp.image = event.simulation.tel[tels].true_image
                disp.cmap = plt.cm.RdBu_r
                disp.add_colorbar()
                event_list.append(run*1000+i)
                plt.savefig(f'/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/images/noFlag_event{run*1000+i}_tels{tels}')

    
    result_event = ','.join(map(str,event_list))
    with open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/output/images_events_{i}.txt", 'a') as fout:
        if result_event:
            fout.write(result_event)
            fout.write(',')








