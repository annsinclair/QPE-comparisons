# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = 'path/to/mrms_files'                  # USER INPUT! location of downloaded data
save_path = '/path/to/store/cleaned_data/mrms.nc' # USER INPUT! location to store cleaned data

# open downloaded data files as one dataset
files = glob.glob(os.path.join(file_path, "*.nc"))
ds = xr.open_mfdataset(files, combine='by_coords')
print('data successfully imported')

# select just the precip variable
mrms_da = ds.VAR_209_6_37_P0_L102_GLL0

# rename variables
mrms_da = mrms_da.rename({'initial_time0_hours': 'time', 'lat_0': 'lat', 'lon_0': 'lon'})

# change from 360 lon to +/- 180
mrms_da = mrms_da.assign_coords(lon=(mrms_da.lon - 360))

# save data as a netCDF
mrms_da.to_netcdf(save_path)
print('netCDF saved to', save_path)