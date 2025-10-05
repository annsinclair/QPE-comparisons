# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = 'path/to/hrrr_files'                  # USER INPUT! location of downloaded data
save_path = '/path/to/store/cleaned_data/hrrr.nc' # USER INPUT! location to store cleaned data

crop = True                                       # USER INPUT! True or False (to crop or not to crop...)

if crop == True:
    # define boundry conditions (OPTIONAL: these values will crop the data to southern California)
    min_x = 100                                   # USER INPUT! left boundary
    min_y = 300                                   # USER INPUT! lower boundary
    max_x = 500                                   # USER INPUT! right boundary
    max_y = 700                                   # USER INPUT! upper boundary

    # loop over each downloaded file and crop
    files = sorted(glob.glob(os.path.join(file_path, "*.nc")))
    da_list = []
    for file in files:
        ds = xr.open_dataset(file)
        da = ds['APCP_P8_L1_GLC0_acc']
        da_crop = da.sel(xgrid_0=slice(min_x, max_x), ygrid_0=slice(min_y, max_y))
        da_list.append(da_crop)
        
else:
    da_list = []
    for file in files:
        ds = xr.open_dataset(file)
        da = ds['APCP_P8_L1_GLC0_acc']
        da_list.append(da)

# combine dataarrays into one
da_full = xr.concat(da_list, dim='initial_time0_hours')

# make sure things are in time order
hrrr_da = da_full
hrrr_da = hrrr_da.sortby(hrrr_da.initial_time0_hours)

# rename
hrrr_rename = hrrr_da.rename({'initial_time0_hours': 'time', 'gridlat_0': 'lat', 'gridlon_0': 'lon'})

# save data as netCDF
hrrr_rename.to_netcdf(save_path)