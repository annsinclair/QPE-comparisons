# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = '/projects/b1045/asinclair/ARs/feb2025/imerg/imerg_ncs'                  # USER INPUT! location of downloaded data
save_path = '/projects/b1045/asinclair/ARs/feb2025/qpe_datasets/imerg.nc' # USER INPUT! location to store cleaned data

# open downloaded data files as one dataset
files = glob.glob(os.path.join(file_path, "*.nc4"))
ds = xr.open_mfdataset(files, combine='by_coords')
print('data successfully imported')

# resample to hourly data
ds_resample = ds.resample(time='1H', label='right').mean()
print('data resampled to hourly')

# select just the precip variable
imerg_da = ds_resample.precipitation

# transpose variables to match with other products (this makes things easier later)
imerg_da = imerg_da.transpose('time', 'lat', 'lon')

# add an hour to time to make hour labels consistent with other products
imerg_da['time'] = imerg_da['time'].astype('datetime64[ns]') #+ np.timedelta64(1, 'h')

# save data as a netCDF
imerg_da.to_netcdf(save_path)
print('netCDF saved to', save_path)