# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = 'path/to/merra2_files'                  # USER INPUT! location of downloaded data
save_path = '/path/to/store/cleaned_data/merra2.nc' # USER INPUT! location to store cleaned data

crop = True                                         # USER INPUT! True or False (to crop or not to crop...)

if crop == True:
    # define bounds of study area, if desired 
    lon_min = -123                                  # USER INPUT! longitude bound 1 (from -180-180)
    lon_max = -114                                  # USER INPUT! longitude bound 2 (from -180-180)
    lat_min = 32                                    # USER INPUT! latitude bound 1 
    lat_max = 38                                    # USER INPUT! latitude bound 2

# open downloaded data files as one dataset
files = sorted(glob.glob(os.path.join(file_path, "*.nc")))
ds = xr.open_mfdataset(files, combine='by_coords')
print('data successfully imported')

# change precip data from mm/s to mm/h
ds['PRECTOTCORR'] = ds['PRECTOTCORR'] * 60 * 60

# add an hour to time to make hour labels consistent with other products
ds['time'] = time_array + np.timedelta64(1, 'h')

if crop == True:
    # crop (OPTIONAL)
    ds = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

# select just the precip variable
merra2_da = ds.PRECTOTCORR

# transpose variables to match with other products (this makes things easier later)
merra2_da = merra2_da.transpose('time', 'lat', 'lon')

# save data as a netCDF
merra2_da.to_netcdf(save_path)
print('netCDF saved to', save_path)