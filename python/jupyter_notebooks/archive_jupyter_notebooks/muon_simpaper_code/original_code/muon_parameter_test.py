from ctapipe.io import SimTelEventSource
from ctapipe.io import HDF5TableWriter
from ctapipe.image import ImageExtractor
from ctapipe.calib import CameraCalibrator
from ctapipe.instrument import CameraGeometry
from ctapipe.visualization import CameraDisplay
from ctapipe.image import TailcutsImageCleaner
from ctapipe.instrument import TelescopeDescription, SubarrayDescription
from ctapipe.image.muon import MuonRingFitter, MuonIntensityFitter
from ctapipe.image.muon import ring_containment, ring_completeness, intensity_ratio_inside_ring, mean_squared_error
from ctapipe.containers import MuonParametersContainer
from ctapipe.containers import MuonHoughContainer
from ctapipe.coordinates import TelescopeFrame, CameraFrame
from astropy.coordinates import SkyCoord

#%matplotlib inline
from tqdm import tqdm
import numpy as np
import glob
from os.path import basename
from sys import argv
#import mpld3
import matplotlib.pyplot as plt
import cv2 as cv
import astropy.units as u

#Full array print
#import sys
#np.set_printoptions(threshold=sys.maxsize)
from Hough_Transform import HoughT
from joblib import Parallel, delayed

#telescope=argv[1]
telescope="sst-astri"
simtel_dir="/media/san/astro/soft/simtelarray/Data/sim_telarray/cta-prod4-"+telescope+"/0.0deg/Data/"
#simtel_dir="/Users/ericamillferre/Desktop/UAB/5è Curs/Treball de Fi de Grau/ctasoft/ctapipe/"
muon_dir=simtel_dir

#simtel_files="muon_15deg_174.681deg_run173___cta-prod4-sst-astri_desert-2180m-LaPalma-sst-astri.simtel.gz"
#simtel_files="muon_*.gz" # Read all .gz files
simtel_files=argv[1]

files = glob.glob(simtel_dir+simtel_files)

def do_loop(i):

    single_file = files[i]
    print('Now treating',single_file)
    
    source = SimTelEventSource( input_url=single_file)

    print('Source', source, source.subarray)
    
    # Define the output file
    #Posar gruix tant a la funcio com al nom del outfile
    outfile = basename(single_file).replace(".gz",".hdf5")
    writer = HDF5TableWriter(muon_dir+outfile, "muons", mode="w")
    
    # These two columns need to be excluded by hand, 
    # because they show variable sizes for different events and cannot be stored in a fixed-sized table
    
    muon_table_name = 'muon_table'
    writer.exclude(muon_table_name, 'prediction')
    writer.exclude(muon_table_name, 'mask')

    extractor_name = 'GlobalPeakWindowSum'
    extractor = ImageExtractor.from_name(extractor_name,subarray=source.subarray)
    calib = CameraCalibrator(subarray=source.subarray, image_extractor=extractor)

    picture_threshold_pe = 7.
    boundary_threshold_pe = 3.
    cleaning = TailcutsImageCleaner(subarray=source.subarray,
                                    picture_threshold_pe=picture_threshold_pe, boundary_threshold_pe=boundary_threshold_pe)

    min_pixels = 8
    pedestal_noise_rms = 1.05 

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
        print ('event: ', event.dl1.tel[tel_id])
        print ('Image Length', len(image))

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
        print ('x,y length:', len(cam.pix_x),len(cam.pix_y))

        plt.figure()

        # iterative ring fit.
        # First use cleaning pixels, then only pixels close to the ring
        # three iterations seems to be enough for most rings
        mask = clean_mask
        for i in range(3):
            ring = ring_fitter(x, y, image, mask)
            dist = np.sqrt((x - ring.center_x)**2 + (y - ring.center_y)**2)
            mask = np.abs(dist - ring.radius) / ring.radius < 0.4

        if np.count_nonzero(mask) <= min_pixels:
            print(f'Skipping event {event_id}:'
                  f' Less then {min_pixels} pixels on ring')
            continue

        if np.isnan([ring.radius.value, ring.center_x.value, ring.center_y.value]).any():
            print(f'Skipping event {event_id}: Ring fit did not succeed')
            continue

        disp = CameraDisplay(cam)
        disp.add_colorbar()
        disp.image = image

        H_pixel_width = CameraGeometry.guess_pixel_width(cam.pix_x.value, cam.pix_y.value)
        H_ring = HoughT(cam.pix_x, cam.pix_y, disp.image, H_pixel_width/2., 0.01, telescope.optics.equivalent_focal_length.value)
        #print(0.017 * u.m / telescope.optics.equivalent_focal_length * 180. / np.pi)
        #wait = input()

        H_radius  = H_ring[4] - H_pixel_width/2.

        dist = np.sqrt((cam.pix_x.value - H_ring[0]) ** 2 + (cam.pix_y.value - H_ring[1]) ** 2)
        H_mask = np.abs(dist - H_radius) / H_radius < 0.4

        # add ring containment, not filled in fit
        border = cam.get_border_pixel_mask()
        fov_radius = np.sqrt(x[border]**2 + y[border]**2).mean()
        containment = ring_containment(
            ring.radius,
            ring.center_x,
            ring.center_y,
            fov_radius,
        )

        H_fov_radius = np.sqrt(cam.pix_x.value[border] ** 2 + cam.pix_y.value[border] ** 2).mean()
        H_containment = ring_containment(
            H_radius,
            H_ring[0],
            H_ring[1],
            H_fov_radius,
        )


        completeness_threshold = 25   #  defaults
        completeness_bins = 16        #  defaults
        completeness = ring_completeness(
            x[mask], y[mask], image[mask],
            ring.radius, ring.center_x, ring.center_y,
            completeness_threshold,  completeness_bins
        )

        H_completeness = ring_completeness(
            cam.pix_x.value[H_mask], cam.pix_y.value[H_mask], image[H_mask],
            H_radius, H_ring[0], H_ring[1],
            completeness_threshold, completeness_bins
        )

        pixel_width = CameraGeometry.guess_pixel_width(x,y)
        #print("witdh ", pixel_width)
        #wait=input()
        ratio_width = 1.5             # defaults
        intensity_ratio = intensity_ratio_inside_ring(
            x[clean_mask], y[clean_mask],
            image[clean_mask],
            ring.radius, ring.center_x, ring.center_y,
            width=ratio_width * pixel_width,
        )

        H_intensity_ratio = intensity_ratio_inside_ring(
            cam.pix_x.value[clean_mask], cam.pix_y.value[clean_mask],
            image[clean_mask],
            H_radius, H_ring[0], H_ring[1],
            width=ratio_width * H_pixel_width,
        )

        mse = mean_squared_error(
            x[clean_mask], y[clean_mask], image[clean_mask],
            ring.radius, ring.center_x, ring.center_y
        )

        H_mse = mean_squared_error(
            cam.pix_x.value[clean_mask], cam.pix_y.value[clean_mask], image[clean_mask],
            H_radius, H_ring[0], H_ring[1]
        )

        params = MuonParametersContainer(
            containment=containment,
            completeness=completeness,
            intensity_ratio=intensity_ratio,
            mean_squared_error=mse
        )
        
        # intensity_fitter does not support a mask yet, set ignored pixels to 0
        H_image = image
        image[~mask] = 0
        H_image[~H_mask] = 0
        intens = intensity_fitter(tel_id,ring.center_x,ring.center_y,ring.radius,
                                image,pedestal=pedestal_noise_rms)

        cam_coord_H = SkyCoord(x=H_ring[0] * u.m, y=H_ring[1] * u.m, frame=camera_frame)
        tel_coord_H = cam_coord_H.transform_to(TelescopeFrame())
        H_intens = intensity_fitter(tel_id, tel_coord_H.fov_lon.deg*u.deg, tel_coord_H.fov_lat.deg*u.deg, H_radius*u.deg/telescope.optics.equivalent_focal_length.value*180./np.pi,
                                  H_image, pedestal=pedestal_noise_rms)

        hough = MuonHoughContainer(
            H_center_x = tel_coord_H.fov_lon.deg,
            H_center_y = tel_coord_H.fov_lat.deg,
            H_radius = H_radius * u.m / telescope.optics.equivalent_focal_length * 180. / np.pi,
            H_width = H_ring[5] * u.m / telescope.optics.equivalent_focal_length * 180. / np.pi,
            H_containment = H_containment,
            H_completeness = H_completeness,
            H_intensity_ratio = H_intensity_ratio,
            H_mean_squared_error = H_mse,
            H_width_intens = H_intens['width'],
            H_impact = H_intens['impact'],
            H_impact_x = H_intens['impact_x'],
            H_impact_y = H_intens['impact_y'],
            H_optical_efficiency = H_intens['optical_efficiency'],
            H_impact_error = H_intens['impact_error'],
            H_phi_error = H_intens['phi_error'],
            H_width_intens_error = H_intens['width_error'],
            H_optical_efficiency_error = H_intens['optical_efficiency_error']
        )

        print(f'Muon fit: r={ring.radius:.2f}'
              f', width={intens.width:.4f}'
              f', efficiency={intens.optical_efficiency:.2%}',
              f', mse={params.mean_squared_error:.2f}',
              f', completeness={params.completeness:.2%}',
              f', r={hough.H_radius:.2f}',
              f', completeness={hough.H_completeness:.2%}'
        )

        print(ring)

        #plt.show()

        #Afegir nous elements

        writer.write(table_name=muon_table_name,
                     containers=[ring,intens,params,event.simulation.shower,hough])

        #plt.scatter(H_ring[0], H_ring[1])
        #plt.scatter(H_ring[2], H_ring[3])
        #plt.show()
        #wait = input("Press enter.")

        cnt = cnt + 1   
        if (max_counter > 0 and cnt == max_counter):
            print ("break\n")
            break
    
    print ('Detected ',cnt,' muons for further analysis')
    writer.close()
    print ('Finished writing ', outfile)

Parallel(n_jobs=3)(delayed(do_loop)(i) for i in range(len(files)))
