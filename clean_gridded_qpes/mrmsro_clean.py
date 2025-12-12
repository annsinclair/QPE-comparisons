# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = '/projects/b1045/asinclair/ARs/feb2025/mrmsro/mrmsro_files'                  # USER INPUT! location of downloaded data
save_path = '/projects/b1045/asinclair/ARs/feb2025/qpe_datasets/mrmsro.nc' # USER INPUT! location to store cleaned data

crop = True                                         # USER INPUT! True or False (to crop or not to crop...)

if crop == True:
    # define bounds of study area, if desired 
    lon_min = -123                                  # USER INPUT! longitude bound 1 (from -180-180)
    lon_max = -114                                  # USER INPUT! longitude bound 2 (from -180-180)
    lat_min = 32                                    # USER INPUT! latitude bound 1 
    lat_max = 38                                    # USER INPUT! latitude bound 2

# import files 
files = sorted(glob.glob(os.path.join(file_path, "*.nc")))

# define list for indivual hour data
da_list = []

# loop through hourly files, clean, add time coordinate
for file in files:
    # open dataset
    ds = xr.open_dataset(file)
    #select precip variable
    da = ds.RadarOnlyQPE01H_P0_L102_GLL0

    # crop to study area
    if crop == True:
        da = da.where(
            ((da.lat_0>=lat_min) & (da.lat_0<=lat_max)) & 
            ((da.lon_0>=(lon_min + 360)) & (da.lon_0<=(lon_max + 360))), drop=True)
        
    da_list.append(da)
print('files imported')

# open downloaded data files as one dataset
da_full = xr.concat(da_list, dim='initial_time0_hours')
print('files combined')
print('data combined')

# rename variables
mrms_da = da_full.rename({'initial_time0_hours': 'time', 'lat_0': 'lat', 'lon_0': 'lon'})

# change from 360 lon to +/- 180
mrms_da = mrms_da.assign_coords(lon=(mrms_da.lon - 360))

# save data as a netCDF
mrms_da.to_netcdf(save_path)
print('netCDF saved to', save_path)