# import libraries
import numpy as np
import xarray as xr
import glob
import os
import re
from datetime import datetime

# define paths
file_path = '/projects/b1045/asinclair/ARs/feb2025/he/he_files'                  # USER INPUT! location of downloaded data
grid_path = '/projects/b1045/asinclair/ARs/feb2025/he/he_grid_file/NPR.GEO.GHE.v1.Navigation.netcdf.gz'              # USER INPUT! location of downloaded data
save_path = '/projects/b1045/asinclair/ARs/feb2025/qpe_datasets/he.nc' # USER INPUT! location to store cleaned data

# define boundry conditions (OPTIONAL: these values will crop the data to southern California)
min_x = 1000                                    # USER INPUT! left boundary
min_y = 1500                                    # USER INPUT! lower boundary
max_x = 1500                                    # USER INPUT! right boundary
max_y = 1900                                    # USER INPUT! upper boundary

# open grid dataset
grid_ds = xr.open_dataset(grid_path)
# crop grid dataset
grid_ds = grid_ds.sel(lines=slice(min_x, max_x), elems=slice(min_y, max_y))
print('grid imported')

# loop over each downloaded files, crop, and set time
da_list = []
files = sorted(glob.glob(os.path.join(file_path, "*.nc")))
for file in files:
    ds = xr.open_dataset(file)
    da = ds['rain']
    
    da_crop = da.sel(lines=slice(min_x, max_x), elems=slice(min_y, max_y))
    
    dt_str = re.search('(\d+)', da_crop.attrs['long_name']).group(0)
    dt = datetime.strptime(dt_str, '%Y%m%d%H%M')
    dt64 = np.datetime64(dt).astype('datetime64[s]')
    da_time = da_crop.expand_dims(dim={'time': [dt64]})

    da_list.append(da_time)

print('files imported')

    
# combine dataarrays into one
da_full = xr.concat(da_list, dim='time')

# merge data with grid dataset
ds_merged = xr.merge([grid_ds, da_full]).set_coords(('latitude', 'longitude'))

# get rid of negative (NaN) values
ds_merged = ds_merged.where(ds_merged['rain'] >= 0.)
print('files combined')

# rename
ds_rename = ds_merged.rename({'lines': 'x', 'elems': 'y', 'latitude': 'lat', 'longitude': 'lon'})

# resample to hourly
ds_resample = ds_rename.resample(time='1H', label='right').mean()
print('data resampled to hourly')

# save data as a netCDF
he_da = ds_resample.rain
he_da.to_netcdf(save_path)
print('netCDF saved to', save_path)