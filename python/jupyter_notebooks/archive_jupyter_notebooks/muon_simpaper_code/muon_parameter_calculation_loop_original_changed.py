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

from tqdm import tqdm
import numpy as np
import glob
from os.path import basename
from sys import argv

simtel_files = ["/Users/vdk/GeneveWork/Muons/data/run101_muon_mst_flash.simtel.gz"]

#for single_file in glob.glob(simtel_dir+simtel_files):
for single_file in simtel_files:   
    print ('Now treating',single_file)
    
    source = SimTelEventSource(input_url=single_file)
    
    print(source, source.subarray)  

    # Define the output file
    outfile = basename(single_file).replace(".gz",".hdf5") 
    #writer = HDF5TableWriter(muon_dir+outfile, "muons", mode="w")
    writer = HDF5TableWriter("/Users/vdk/GeneveWork/Muons/data/output/" + outfile, "muons", mode="w")
    
    # These two columns need to be excluded by hand, 
    # because they show variable sizes for different events and cannot be stored in a fixed-sized table
    
    muon_table_name = 'muon_table'
    writer.exclude(muon_table_name, 'prediction')
    writer.exclude(muon_table_name, 'mask')

    #extractor_name = 'GlobalPeakWindowSum'
    extractor_name = 'FlashCamExtractor'
    
    extractor = ImageExtractor.from_name(extractor_name,subarray=source.subarray)
    calib = CameraCalibrator(subarray=source.subarray, image_extractor=extractor)

    picture_threshold_pe = 10.
    boundary_threshold_pe = 5.
    cleaning = TailcutsImageCleaner(subarray=source.subarray,
                                    picture_threshold_pe=picture_threshold_pe, boundary_threshold_pe=boundary_threshold_pe)

    min_pixels = 10
    pedestal_noise_rms = 1.1 

    ring_fitter = MuonRingFitter(fit_method="taubin")
    #ring_fitter = MuonRingFitter(fit_method="kundu_chaudhuri")
    intensity_fitter = MuonIntensityFitter(subarray=source.subarray)

    max_counter = -1  # for testing, set it to a small positive number
    cnt = 0
    tel_id = 1  # Here, because we have simulated only one telescope!

    for event in tqdm(source, desc='detecting muons'):

        #print (event)

        event_id = event.index.event_id
        calib(event)    
        image = event.dl1.tel[tel_id].image
        #print (image)

        clean_mask = cleaning(tel_id, image)
    
        if np.count_nonzero(clean_mask) <= min_pixels:
            print(f'Skipping event {event_id}:'
                  f' has less then {min_pixels} pixels after cleaning')
            continue
    
        telescope = source.subarray.tel[tel_id]
        cam = telescope.camera.geometry
       
        camera_frame = CameraFrame(focal_length=telescope.optics.equivalent_focal_length,
                                    rotation=cam.cam_rotation)
        cam_coords = SkyCoord(x=cam.pix_x, y=cam.pix_y, frame=camera_frame)
        tel_coord = cam_coords.transform_to(TelescopeFrame())
    
        x, y = tel_coord.fov_lon, tel_coord.fov_lat

        # iterative ring fit.
        # First use cleaning pixels, then only pixels close to the ring
        # three iterations seems to be enough for most rings
        mask = clean_mask
        for i in range(3):
            ring = ring_fitter(x, y, image, mask)
            dist = np.sqrt((x - ring.center_fov_lon)**2 + (y - ring.center_fov_lat)**2)
            mask = np.abs(dist - ring.radius) / ring.radius < 0.4

        if np.count_nonzero(mask) <= min_pixels:
            print(f'Skipping event {event_id}:'
                  f' Less then {min_pixels} pixels on ring')
            continue

        if np.isnan([ring.radius.value, ring.center_fov_lon.value, ring.center_fov_lat.value]).any():
            print(f'Skipping event {event_id}: Ring fit did not succeed')
            continue

        # add ring containment, not filled in fit
        border = cam.get_border_pixel_mask()
        fov_radius = np.sqrt(x[border]**2 + y[border]**2).mean()
        containment = ring_containment(
            ring.radius,
            ring.center_fov_lon,
            ring.center_fov_lat,
            fov_radius,
        )

        completeness_threshold = 30   #  defaults
        completeness_bins = 30        #  defaults
        completeness = ring_completeness(
            x, y, image,
            ring.radius, ring.center_fov_lon, ring.center_fov_lat,
            completeness_threshold,  completeness_bins
        )

        pixel_width = CameraGeometry.guess_pixel_width(x,y)
        ratio_width = 1.5             # defaults
        intensity_ratio = intensity_ratio_inside_ring(
            x[clean_mask], y[clean_mask],
            image[clean_mask],
            ring.radius, ring.center_fov_lon, ring.center_fov_lat,
            width=ratio_width * pixel_width,
        )

        mse = mean_squared_error(
            x[clean_mask], y[clean_mask], image[clean_mask],
            ring.radius, ring.center_fov_lon, ring.center_fov_lat
        )

        params = MuonParametersContainer(
            containment=containment,
            completeness=completeness,
            intensity_ratio=intensity_ratio,
            mean_squared_error=mse
        )
        
        # intensity_fitter does not support a mask yet, set ignored pixels to 0
        image[~mask] = 0

        intens = intensity_fitter(tel_id,ring.center_fov_lon,ring.center_fov_lat,ring.radius,
                                image,pedestal=pedestal_noise_rms)

        print(f'Muon fit: r={ring.radius:.2f}'
              f', width={intens.width:.4f}'
              f', efficiency={intens.optical_efficiency:.2%}',
              f', mse={params.mean_squared_error:.2f}',
              f', completeness={params.completeness:.2%}'
        )

        print (ring)
    
        writer.write(table_name=muon_table_name,
                     containers=[ring,intens,params,event.simulation.shower])
 
        cnt = cnt + 1   
        if (max_counter > 0 and cnt == max_counter):
            break
    
    print ('Detected ',cnt,' muons for further analysis')
    writer.close()
    print ('Finished writing ', outfile)
