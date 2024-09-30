import sys
from astropy.io import ascii
import numpy as np
import pandas as pd
from traitlets.config import Config
from ctapipe.image import ImageProcessor
from ctapipe.image.muon import MuonProcessor
from ctapipe.instrument import CameraGeometry
from ctapipe.io import EventSource
from ctapipe.calib import CameraCalibrator
from traitlets.config.loader import Config
from traitlets.config import Config
from traitlets.config import Config


# all muon rings among stereo protons for runs 3978-4000
final_rings = [78124, 78437, 79331, 80266, 81137, 82039, 82691, 84192, 84560, 84631, 86287, 86345, 86590, 86633, 87027, 87511, 87597, 88049, 88103, 88130, 88524, 88598, 88599, 88647, 89104, 89236, 90093, 90324, 90493, 90635, 91012, 91662, 93161, 94747, 96593, 97606, 98657, 99694]
print(len(final_rings))
new_final_rings = final_rings

#for i in final_rings:
#    new_final_rings.append(int(str(39)+str(i)))

print(len(new_final_rings))