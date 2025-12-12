# import libraries
import numpy as np
import xarray as xr
import glob
import os


Download = True                                   # USER INPUT! True or False (to download or not to download...)

# define paths
file_path = '/projects/b1045/asinclair/ARs/feb2025/era5/era5_files/era5.nc'                   # USER INPUT! location of downloaded data (OR to put downloaded data)
save_path = '/projects/b1045/asinclair/ARs/feb2025/era5/era5_clean.nc'  # USER INPUT! location to store cleaned data

if Download == True:                               
# download data------------>OPTIONAL! (if data is not already downloaded)
# NOTE: change dates and area to fit needs
# see https://cds.climate.copernicus.eu/how-to-api for more information
    import cdsapi
    dataset = "reanalysis-era5-single-levels"
    request = {
        "product_type": ["reanalysis"],
        "variable": ["total_precipitation"],
        "year": ["2025"],
        "month": ["02"],
        "day": [
            "12", "13",
            "14", "15",
        ],
        "time": [
            "00:00", "01:00", "02:00",
            "03:00", "04:00", "05:00",
            "06:00", "07:00", "08:00",
            "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00",
            "15:00", "16:00", "17:00",
            "18:00", "19:00", "20:00",
            "21:00", "22:00", "23:00"
        ],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [38, -123, 32, -114]
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request).download(file_path)
    
    print('download complete')

# open downloaded data 
ds = xr.open_dataset(file_path)
print('data successfully imported')

# multiply precip field by 1000 to convert from m to mm
era5_da = ds.tp * 1000

# rename variables
era5_da = era5_da.rename({'valid_time': 'time', 'latitude': 'lat', 'longitude': 'lon'})

# save data as a netCDF
era5_da.to_netcdf(save_path)
print('netCDF saved to', save_path)