# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = '/projects/b1045/asinclair/ARs/feb2025/nldas2/nldas2_ncs'                  # USER INPUT! location of downloaded data
save_path = '/projects/b1045/asinclair/ARs/feb2025/qpe_datasets/nldas2.nc' # USER INPUT! location to store cleaned data

# open downloaded data files as one dataset
files = sorted(glob.glob(os.path.join(file_path, "*.nc4")))
ds = xr.open_mfdataset(files, combine='by_coords')
print('data successfully imported')

# select just the precip variable
nldas2_da = ds.Rainf

# transpose variables to match with other products (this makes things easier later)
nldas2_da = nldas2_da.transpose('time', 'lat', 'lon')

# save data as a netCDF
nldas2_da.to_netcdf(save_path)
print('netCDF saved to', save_path)