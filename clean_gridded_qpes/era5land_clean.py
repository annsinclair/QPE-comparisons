# import libraries
import numpy as np
import xarray as xr
import glob
import os

Download = False                                       # USER INPUT! True or False (to download or not to download...)

# define paths
file_path = 'path/to/era5land_files'                   # USER INPUT! location of downloaded data (OR to put downloaded data)
save_path = '/path/to/store/cleaned_data/era5land.nc'  # USER INPUT! location to store cleaned data

if Download == True:
# download data------------>OPTIONAL! (if data is not already downloaded)
# NOTE: change dates and area to fit needs
# see https://cds.climate.copernicus.eu/how-to-api for more information
    import cdsapi
    c = cdsapi.Client()
    c.retrieve(
        'reanalysis-era5-land',
        {
            'time':[
                '00:00','01:00','02:00',
                '03:00','04:00','05:00',
                '06:00','07:00','08:00',
                '09:00','10:00','11:00',
                '12:00','13:00','14:00',
                '15:00','16:00','17:00',
                '18:00','19:00','20:00',
                '21:00','22:00','23:00'
            ],
            'day':['27','28','29'],
            'month':'01',
            'year':'2021',
            'variable':'total_precipitation',
            "data_format": "netcdf",
            "download_format": "unarchived"
        },
        file_path)
    
    print('download complete')

# open downloaded data 
ds = xr.open_dataset(file_path)
print('data successfully imported')

# get times
time_array = pd.to_datetime(ds.valid_time.values)

# era5land precip data is cumulative, and resets every day 
# we need to make some changes to calculate hourly intensities 

def calculate_intensities(array):
    time_array = pd.to_datetime(array.valid_time.values)
    reset_indices = np.where(time_array.hour == 1)[0]
    
    cumsum_array = array.copy() * 1000
    cumsum_array[0] = 0
    
    for reset_index in reset_indices[::-1]:
        array_pre = cumsum_array[:reset_index]
        array_post = cumsum_array[reset_index:]
        
        array_post_summed = array_post + array_pre[-1]
        cumsum_array = np.concatenate((array_pre, array_post_summed))
        
    int_array = np.diff(cumsum_array, prepend=0)
    return int_array

# apply intensity fuction
era5land_da = xr.apply_ufunc(
    calculate_intensities,
    ds.tp,
    input_core_dims=[['valid_time']],
    output_core_dims=[['valid_time']],
    vectorize=True
)

# rename variables
era5land_da = era5land_da.rename({'valid_time': 'time', 'latitude': 'lat', 'longitude': 'lon'})

# save data as a netCDF
era5land_da.to_netcdf(save_path)
print('netCDF saved to', save_path)
