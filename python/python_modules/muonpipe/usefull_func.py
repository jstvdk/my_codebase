import copy
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.table import Table

def hist_wo_outliers(array_original, outlier_value=1000, show_outliers = False, mean_line = False, **kwargs):
    """
    Function to build histograms with option to process outliers
    
    Arguments
    ---------
    
    array_original - [list] - should be dimensionless
    
    outlier_value - int - value of outlier
    
    show_outliers - boolean - outlier visulation
    
    mean_line - boolean - show mean of the distribution
     
    """


    array = copy.copy(array_original)
    outliers = [value for value in array if value >= outlier_value]
    array = [value for value in array if value < outlier_value]
    if not show_outliers:
        z,x,c = plt.hist(array, **kwargs)
    else:
        outlier_hist = [outlier_value for _ in outliers]
        array.extend(outlier_hist)
        print(f"Number of outliers = {len(outlier_hist)}")
        z,x,c = plt.hist(array, **kwargs)
    plt.grid(alpha = 0.5)
    if mean_line:
        plt.axvline(x=np.mean(array), color='r', linestyle='--')
    print(f"Mean value of the x_axis = {np.mean(array)} \nStandard deviation = {np.std(array)}")
    

def atmo_thick(height, make_plot=False):
    """ 
    Function that returns atmospheric thickness in g/cm^2
    
    Arguments
    ---------
    height - [m]
        Height for which thickness should be calculated
        
    Returns
    -------
    value of the thickness [g/cm2] for given height
    """
    atmospheric_thickness = [1036, 920, 818, 726, 643, 568, 499, 438, 383, 333, 288, 249, 213, 182, 155, 132, 112, 95, 80, 67, 57]
    altitude = [i for i in range(21)]
    xvals = np.linspace(0, 20, 20000)

    interpolated_thickness = np.interp(xvals, altitude, atmospheric_thickness)
    if make_plot:
        plt.figure()
        plt.scatter(xvals, interpolated_thickness, alpha = 0.2)
        plt.grid()
    
    return interpolated_thickness[height]

import math

def cherenkov_angle(muon_energy_eV, refractive_index=1.000293):
    """
    Calculate the Cherenkov angle for a given muon energy and refractive index.

    Parameters:
    - muon_energy_eV (float): The energy of the muon in electron volts (eV).
    - refractive_index (float, optional): The refractive index of the medium. Default is 1.000293.

    Returns:
    - theta_C_degrees (float): The Cherenkov angle in degrees.

    Raises:
    - None

    """
    # Constants
    c = 299792458  # speed of light in m/s
    muon_rest_mass_MeV = 105.66  # rest mass of muon in MeV
    eV_to_MeV = 1e-6  # conversion factor from eV to MeV
    
    # Convert muon energy from eV to MeV
    muon_energy_MeV = muon_energy_eV * eV_to_MeV
    
    # Check if the energy is sufficient for Cherenkov radiation
    if muon_energy_MeV <= muon_rest_mass_MeV:
        return "Energy too low for Cherenkov radiation."
    
    # Calculate the momentum p
    p = math.sqrt((muon_energy_MeV)**2 - (muon_rest_mass_MeV)**2)
    
    # Calculate beta
    beta = p / muon_energy_MeV
    
    # Check if Cherenkov condition is met
    if beta * refractive_index <= 1:
        return "Muon velocity too low for Cherenkov radiation in this medium."
    
    # Calculate Cherenkov angle
    cos_theta_C = 1 / (beta * refractive_index)
    theta_C = math.acos(cos_theta_C)
    
    # Convert angle from radians to degrees
    theta_C_degrees = math.degrees(theta_C)
    
    return theta_C_degrees

def plot_cherenkov_angle_distribution(min_energy_eV, max_energy_eV, num_points, refractive_index=1.000293, plot_option=False):
    """
    Plots the Cherenkov angle distribution as a function of muon energy.

    Parameters:
    - min_energy_eV (float): The minimum energy in electron volts (eV) for the muon.
    - max_energy_eV (float): The maximum energy in electron volts (eV) for the muon.
    - num_points (int): The number of points to generate between the minimum and maximum energy.
    - refractive_index (float, optional): The refractive index of the medium. Default is 1.000293.
    - plot_option (bool, optional): Whether to plot the distribution. Default is False.

    Returns:
    - energies_GeV (numpy.ndarray): An array of muon energies in gigaelectron volts (GeV).
    - angles (list): A list of Cherenkov angles in degrees corresponding to the muon energies.

    Example usage:
    >>> min_energy_eV = 1e6
    >>> max_energy_eV = 1e9
    >>> num_points = 100
    >>> refractive_index = 1.000293
    >>> plot_option = True
    >>> energies_GeV, angles = plot_cherenkov_angle_distribution(min_energy_eV, max_energy_eV, num_points, refractive_index, plot_option)
    """

    energies_eV = np.logspace(np.log10(min_energy_eV), np.log10(max_energy_eV), num_points)
    energies_GeV = energies_eV * 1e-9  # Convert eV to GeV
    angles = []

    for energy in energies_eV:
        angle = cherenkov_angle(energy, refractive_index)
        if angle is not None:
            angles.append(angle)
        else:
            angles.append(0)  # Append 0 for energies not producing Cherenkov radiation

    if plot_option:
        plt.plot(energies_GeV, angles, label='Cherenkov Angle')
        plt.xscale('log')
        plt.xlabel('Muon Energy (GeV)')
        plt.ylabel('Cherenkov Angle (degrees)')
        plt.title('Cherenkov Angle Distribution as a Function of Muon Energy')
        plt.legend()
        plt.show()

    return energies_GeV, angles

def get_muon_parameters(listdir, **kwargs):
    """
    Extracts and filters muon parameters from a list of FITS files.
    Parameters:
    -----------
    listdir : list of str
        List of file paths to the FITS files to be processed.
    **kwargs : dict
        Dictionary of cuts to be applied to the data. The keys should be the column names,
        and the values should be tuples of the form (cut_value, cut_type), where:
            - cut_value : float
                The threshold value for the cut.
            - cut_type : str
                The type of cut to apply. Should be either 'lower' (keep values greater than cut_value)
                or 'upper' (keep values less than cut_value).
    Returns:
    --------
    pandas.DataFrame
        A concatenated DataFrame containing the filtered data from all the FITS files.
        
    Example of usage:

    test_df_frame = get_muon_parameters(listdir, muon_efficiency=(1, 'upper'), size_outside=(500, 'upper'))
    """

    filtered_data_list = []

    for fits_file in listdir:
        # Read the FITS file into an Astropy Table
        dat = Table.read(fits_file, format='fits')
        
        # Convert 'good_ring' column to boolean if it exists
        if 'good_ring' in dat.colnames:
            dat['good_ring'] = dat['good_ring'].astype(bool)
        
        # Convert the Astropy Table to a Pandas DataFrame
        df = dat.to_pandas()
        
        # Apply the cuts (filters)
        # Start by setting a mask to all True (no filtering)
        mask = pd.Series([True] * len(df))
        
        # Iterate over the cuts passed via kwargs
        for column, (cut_value, cut_type) in kwargs.items():
            if cut_type == 'lower':
                mask &= df[column] > cut_value
            elif cut_type == 'upper':
                mask &= df[column] < cut_value
            else:
                raise ValueError(f"Invalid cut type: {cut_type}. Use 'upper' or 'lower'.")
        
        # Filter the dataframe based on the combined mask
        df_good_data = df[mask]
        
        # Append the filtered data to the list
        filtered_data_list.append(df_good_data)
    
    # Return the list of filtered dataframes
    return pd.concat(filtered_data_list, ignore_index=True)\
    
