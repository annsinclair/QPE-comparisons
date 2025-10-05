# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = 'path/to/persiann_files'                  # USER INPUT! location of downloaded data
save_path = '/path/to/store/cleaned_data/persiann.nc' # USER INPUT! location to store cleaned data

# open downloaded data file (only 1 for PERSIANN)
ds = xr.open_dataset(file_path)
print('data successfully imported')

# get rid of negative (NaN) values
ds_masked = ds.where(ds['precip'] != -99.)

# select just the precip variable
persiann_da = ds_masked.precip

# rename variables
persiann_da = persiann_da.rename({'datetime': 'time'})

# add an hour to time to make hour labels consistent with other products
persiann_da['time'] = persiann_da['time'] + np.timedelta64(1, 'h')

# save data as a netCDF
persiann_da.to_netcdf(save_path)
print('netCDF saved to', save_path)