from Calibration.core.calibration import Calibration
from Calibration.core.device import Device
from Calibration.core.spectrum import Spectrum
from Calibration.core.standard import Standard
from Calibration.core.series import Series

from typing import List, Dict
import re
import numpy as np
import pandas as pd
from datetime import datetime


def parse_CalibrationData(
    path_standard: str,
    path_spectrum: str,
    species_id,
    wavelengths,
    concentrations: List[float],
    concentration_unit,
    device_manufacturer: str,
    device_model: str,
    spectrum_reactant_concentration: float,
    ) -> Dict[float, Calibration]:

    # Define parameters for parser
    temperature_unit = 'C'

    # Read and parse
    df_standard = read_photometer(path_standard)
    
    # Format df_standard and extract metadata
    metadata_row = str(df_standard.iloc[-1].values)
    date = re.findall(r'\d{4}/\d{2}/\d{2}', metadata_row)[0]
    pH = re.findall(r'\d\.\d\+\d\.\d', metadata_row)[0]
    pH = [float(x) for x in pH.split("+")]

    df_standard = df_standard.loc[13:18]
    df_standard = df_standard.reset_index().drop(columns="index")

    # array manipulation to get measurement data
    standard_absorption = np.array([])
    standard_data = df_standard.values
    for i, row in enumerate(standard_data):
        standard_data = str(row).split("\\t")
        standard_data = [string_to_float(x) for x in standard_data]

        if i == 0:
            temperature = standard_data[0]
            standard_data = standard_data[1:]
            standard_absorption = np.append(standard_absorption, standard_data)
        else:
            standard_absorption = np.append(standard_absorption, standard_data)
    
    standard_absorption = standard_absorption[~np.isnan(standard_absorption)]
    standard_absorption = standard_absorption.reshape(6,24)

    # Reshape into (pH, wavelength, replicates, concentrations)
    standard_absorption = blockshaped(standard_absorption, 3, 12).reshape(2,2,3,12)

    # Map pH and corresponding mesurement data into dict
    standard_data_dict = dict(zip(pH, standard_absorption))

    # Spectrum 
    df_spectrum = read_photometer(path_spectrum)

    metadata_row = str(df_spectrum.iloc[-1].values)
    date = re.findall(r'\d{4}/\d{2}/\d{2}', metadata_row)[0]
    pH_spectrum = re.findall(r'\d\.\d\+\d\.\d', metadata_row)[0]
    pH_spectrum = [float(x) for x in pH_spectrum.split("+")]

    if pH_spectrum != pH:
        raise ValueError(
            f"pH of files do not match. Check following files:\n{path_standard}\n{path_spectrum}")

    df_spectrum = df_spectrum.loc[13:87]
    df_spectrum = df_spectrum.reset_index().drop(columns="index")
    df_spectrum = df_spectrum.applymap(tab_split)

    spectrum_data = df_spectrum.values.tolist()
    for i, wavelength in enumerate(spectrum_data):
        spectrum_data[i] = list(filter(None, wavelength[0]))

    data = np.array(spectrum_data)
    spectrum_wavelengths = data[:,0]
    spectrum_absorption = data[:,2:].T

    spectrum_data_dict = dict(zip(pH_spectrum, spectrum_absorption))


    ### Map data to calibration datamodel instance ### 
    # Define photometer meta-data
    device = Device(
        manufacturer=device_manufacturer,
        model=device_model)

    # Create instance of calibration data-model
    # Since each instance of the datamodel only deals with one pH, two instances are created in this case.
    instance_dict = {}
    for pH_value, absorbance_data in standard_data_dict.items():

        # Create instance of data model
        instance = Calibration(
            reactant_id=species_id,
            pH=pH_value,
            date=date,
            device=device,
            temperature=temperature,
            temperature_unit=temperature_unit)

        # Create instances of 'Standard' for both wavelengths
        standard_curves = []
        for i, (wavelength, data) in enumerate(zip(wavelengths, absorbance_data)):
            
            absorption_series = []
            for replicate in absorbance_data[i]:
                absorption_series.append(Series(
                    values=list(replicate)))
            instance.add_to_standard(
                concentration=concentrations,
                wavelength=wavelength,
                concentration_unit=concentration_unit,
                absorption=absorption_series
            )

            standard_curve = Standard(
                    wavelength=wavelength,
                    concentration=concentrations,
                    concentration_unit=concentration_unit
                )
            # Add measurerment data of the standards
            for replicate in data:
                standard_curve.add_to_absorption(list(replicate))

            standard_curves.append(standard_curve)

        # Add absorption spectrum
        spectrum = Spectrum(
            concentration=spectrum_reactant_concentration,
            concentration_unit=concentration_unit,
            wavelength=spectrum_wavelengths.tolist())

        spectrum.add_to_absorption(spectrum_data_dict[pH_value].tolist())

        instance.spectrum = spectrum
            
        # Add sub-classes of the datamodel to the corresponding parent attributes of the datamodel
        

        # Manage the instances in for of a dict
        instance_dict[pH_value] = instance

    return instance_dict

def parse_measurement(path: str) -> Dict:

    # Read raw data, parse metadata
    df = read_photometer(path)
    metadata_row = (str(df.iloc[-1].values))
    date = re.findall(r'\d{4}/\d{2}/\d{2}', metadata_row)[0]
    pH = float(re.findall(r'\d\.\d', metadata_row)[0])
    
    df = df.iloc[13:-9].reset_index().drop(columns="index")
    df = df.applymap(tab_split)
    initial_substrates=[0,5,10,15,25,50,75,100,150,200]
    time = []
    temperature = []
    array = []

    # Extract measurement data
    for index, row in df.iterrows():
        if index % 6 == 0:
            time.append(row.values[0][0])

            temperature.append(row.values[0][1])
            df.loc[index, "##BLOCKS= 2"] = row.values[0][2:]
    
        data = row.values[0]
        array.append([string_to_float(x) for x in data])

    # Cleaning and restructuring of data
    array = np.array(array)
    array = array[~np.isnan(array)]
    array = array.reshape(11,6,20)
    array = array.swapaxes(0,2)

    #(wavelength, concentration, control, replicates, data)
    array = array.reshape((2,10,2,3,11))
    
    #(wavelength, control, concentration, replicates, data)
    array = array.swapaxes(1,2)

    substrate = array[0][0]
    substrate_control = array[0][1]
    product = array[1][0]
    product_control = array[1][0]

    measurements_product_control = []
    for data, init_substrate in zip(product_control, initial_substrates):
        measurement = {}
        measurement["initial_substrate"] = 0
        reps = []
        for replicate in data:
            rep_dict = {}
            rep_dict["replicate"] = replicate.tolist()
            reps.append(rep_dict)
        measurement["data"] = reps
        
        measurements_product_control.append(measurement)

    measurements_substrate_control = []
    for data, init_substrate in zip(substrate_control, initial_substrates):
        measurement = {}
        measurement["initial_substrate"] = init_substrate
        reps = []
        for replicate in data:
            rep_dict = {}
            rep_dict["replicate"] = replicate.tolist()
            reps.append(rep_dict)
        measurement["data"] = reps
        
        measurements_substrate_control.append(measurement)

    measurements_substrate = []
    for data, init_substrate in zip(substrate, initial_substrates):
        measurement = {}
        measurement["initial_substrate"] = init_substrate
        reps = []
        for replicate in data:
            rep_dict = {}
            rep_dict["replicate"] = replicate.tolist()
            reps.append(rep_dict)
        measurement["data"] = reps
        
        measurements_substrate.append(measurement)

    measurements_product = []
    for data in product:
        measurement = {}
        measurement["initial_substrate"] = 0
        reps = []
        for replicate in data:
            rep_dict = {}
            rep_dict["replicate"] = replicate.tolist()
            reps.append(rep_dict)
        measurement["data"] = reps
        
        measurements_product.append(measurement)

    data_dict = {
        "pH": pH,
        "name": f"ABTS oxidation pH {pH} and {temperature[0]}C",
        "date": str(datetime(*[int(x) for x in date.split("/")],)),
        "time": [to_seconds(x) for x in time],
        "temperature": [float(x) for x in temperature][0],
        "measurements_substrate": measurements_substrate,
        "measurements_product": measurements_product,
        "measurements_product_control": measurements_product_control,
        "measurements_product_control": measurements_product_control,
    }
    return data_dict

# Helper functions

# Slicing of arrays
def blockshaped(arr, nrows, ncols):
        """
        Return an array of shape (n, nrows, ncols) where
        n * nrows * ncols = arr.size

        If arr is a 2D array, the returned array should look like n subblocks with
        each subblock preserving the "physical" layout of arr.
        """
        h, w = arr.shape
        assert h % nrows == 0, f"{h} rows is not evenly divisible by {nrows}"
        assert w % ncols == 0, f"{w} cols is not evenly divisible by {ncols}"
        return (arr.reshape(h//nrows, nrows, -1, ncols)
                .swapaxes(1,2)
                .reshape(-1, nrows, ncols))


def read_photometer(path) -> pd.DataFrame:
        return pd.read_csv(
                path, 
                sep='delimiter', 
                encoding='utf-16', 
                engine='python')


def string_to_float(string: str) -> float:
        number = re.sub(r'[^0-9.]', '', string)
        if len(number) == 0:
            return float('nan')
        else:
            return float(number)

def tab_split(string: str) -> list:
        return string.split("\t")


def to_seconds(string: str) -> List[int]:
        time = datetime.strptime(string, "%H:%M:%S").time()
        return time.hour*3600 + time.minute*60 + time.second


if __name__ == "__main__":
    res = parse_CalibrationData(
        path_standard="/Users/maxhaussler/Dropbox/master_thesis/data/sdRDM_ABTS_oxidation/StandardData/pH 3.0+3.5 25deg standards.txt",
        path_spectrum="/Users/maxhaussler/Dropbox/master_thesis/data/sdRDM_ABTS_oxidation/SpectrumData/pH 3.0+3.5 25deg scan.txt",
        species_id="s1",
        wavelengths=[340, 420],
        concentrations=[0,5,10,15,25,50,75,100,125,150,175,200],
        concentration_unit="uM",
        device_manufacturer="bla",
        device_model="gut",
        spectrum_reactant_concentration=1.3
    )

    print(res[3.0].spectrum)