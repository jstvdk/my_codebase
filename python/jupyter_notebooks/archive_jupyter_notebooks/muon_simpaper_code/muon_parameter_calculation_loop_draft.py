#!/Users/vdk/mambaforge/envs/cta/bin/python
from ctapipe.io import SimTelEventSource
from ctapipe.io import HDF5TableWriter
from ctapipe.image import ImageExtractor
from ctapipe.calib import CameraCalibrator
from ctapipe.instrument import CameraGeometry
from ctapipe.image import TailcutsImageCleaner
from ctapipe.instrument import TelescopeDescription, SubarrayDescription
from ctapipe.image.muon import MuonRingFitter, MuonIntensityFitter
from ctapipe.image.muon import ring_containment, ring_completeness, intensity_ratio_inside_ring, mean_squared_error
from ctapipe.containers import MuonParametersContainer
from ctapipe.coordinates import TelescopeFrame, CameraFrame
from astropy.coordinates import SkyCoord

from traitlets.config.loader import Config, FileConfigLoader, JSONFileConfigLoader
from ctapipe.image import ImageProcessor
from ctapipe.image.muon import MuonProcessor

from tqdm import tqdm
import numpy as np
import glob
from os.path import basename
from sys import argv

#telescope=argv[1]
#simtel_dir="/media/san/astro/soft/simtelarray/Data/sim_telarray/cta-prod4-"+telescope+"/0.0deg/Data/"
#muon_dir=simtel_dir

#simtel_files="muon_60deg_84.6805deg_run*___cta-prod4-sst-astri_desert-2180m-LaPalma-sst-astri.simtel.gz"
#simtel_files=argv[2]
int_cut = 1
min_pixel = 30

muon_processor_config = Config({
                                "MuonProcessor": {
                                    "RingQuery": {
                                        "quality_criteria" : [["intensity_check",f"np.abs(parameters.intensity_ratio - 1) < {int_cut}"],
                                                        ["ring_containment", "parameters.containment > 0.1"],
                                                        ["ring_completeness", "parameters.completeness > 0.1"]]},
                                    "ImageParameterQuery" :{
                                        "quality_criteria" : [["min_pixels", f"dl1_params.morphology.n_pixels > {min_pixel}"],
                                                        ["min_intensity", "dl1_params.hillas.intensity > 500"]]}}})

simtel_files = ["/Users/vdk/GeneveWork/Muons/data/run101_muon_mst_flash.simtel.gz"]
simtel_files = ["/Users/vdk/GeneveWork/Muons/data/run101_muon_mst_nectar.simtel.gz"]
simtel_files = ["/Users/vdk/GeneveWork/Muons/data/run401_muon_lst.simtel.gz"]

#for single_file in glob.glob(simtel_dir+simtel_files):
for single_file in simtel_files:   
    print ('Now treating',single_file)
    
    source = SimTelEventSource(input_url=single_file)

    print(source, source.subarray)  

    # Define the output file
    outfile = basename(single_file).replace(".gz",".hdf5") 
    #writer = HDF5TableWriter(muon_dir+outfile, "muons", mode="w")
    writer = HDF5TableWriter("/Users/vdk/GeneveWork/Muons/data/output_calibpipe/" + outfile, "muons", mode="w")
    
    # These two columns need to be excluded by hand, 
    # because they show variable sizes for different events and cannot be stored in a fixed-sized table
    
    muon_table_name = 'muon_table'
    writer.exclude(muon_table_name, 'prediction')
    writer.exclude(muon_table_name, 'mask')

    min_pixels = 10
    pedestal_noise_rms = 1.1 


    max_counter = -1  # for testing, set it to a small positive number
    cnt = 0
    tel_id = 1  # Here, because we have simulated only one telescope!
    
    image_processor = ImageProcessor(source.subarray)
    muon_processor = MuonProcessor(source.subarray, config = Config(muon_processor_config))
    
    # For NectarCam and LST should work like this
    calib = CameraCalibrator(image_extractor_type="GlobalPeakWindowSum",subarray = source.subarray, config = Config(muon_processor_config))
    
    # For FlashCam need another extractor:
    #calib = CameraCalibrator(image_extractor_type="FlashCamExtractor",subarray = source.subarray, config = Config(muon_processor_config))

    for event in tqdm(source, desc='detecting muons'):
        #print(event)

        event_id = event.index.event_id
        
        calib(event)
        
        image_processor(event)
        muon_processor(event)
        

        ring = event.muon.tel[tel_id].ring, 
        intens = event.muon.tel[tel_id].efficiency, 
        params = event.muon.tel[tel_id].parameters
        print(type(ring))
        
        # print(f"ring pre = {ring} and {type(ring)}")
        # #values_tuple = tuple(q.to_value() for q in ring)
        # print(f"ring post = {values_tuple} and {type(values_tuple)}")
        print(f"efficiency = {event.muon.tel[tel_id].efficiency} and type = {type(event.muon.tel[tel_id].efficiency)}")
        print(f"ring = {event.muon.tel[tel_id].ring}")
        print(f"parameters = {event.muon.tel[tel_id].parameters}")
        writer.write(table_name=muon_table_name,
                   containers=[event.muon.tel[tel_id].ring, event.muon.tel[tel_id].efficiency, event.muon.tel[tel_id].parameters,event.simulation.shower])
 
        cnt = cnt + 1   
        if (max_counter > 0 and cnt == max_counter):
            break
    
    print ('Detected ',cnt,' muons for further analysis')
    writer.close()
    print ('Finished writing ', outfile)
