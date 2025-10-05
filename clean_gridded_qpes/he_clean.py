# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = 'path/to/he_files'                  # USER INPUT! location of downloaded data
grid_path = 'path/to/he_grid_file'              # USER INPUT! location of downloaded data
save_path = '/path/to/store/cleaned_data/he.nc' # USER INPUT! location to store cleaned data

# define boundry conditions (OPTIONAL: these values will crop the data to southern California)
min_x = 1000                                    # USER INPUT! left boundary
min_y = 1500                                    # USER INPUT! lower boundary
max_x = 1500                                    # USER INPUT! right boundary
max_y = 1900                                    # USER INPUT! upper boundary

# open grid dataset
grid_ds = xr.open_dataset(grid_path)
# crop grid dataset
grid_ds = grid_ds.sel(lines=slice(min_x, max_x), elems=slice(min_y, max_y))

# loop over each downloaded files, crop, and set time
da_list = []
files = sorted(glob.glob(os.path.join(file_path, "*.gz")))
for file in files:
    ds = xr.open_dataset(file)
    da = ds['rain']
    
    da_crop = da.sel(lines=slice(min_x, max_x), elems=slice(min_y, max_y))
    
    dt_str = re.search('(\d+)', da_crop.attrs['long_name']).group(0)
    dt = datetime.strptime(dt_str, '%Y%m%d%H%M')
    dt64 = np.datetime64(dt).astype('datetime64[s]')
    da_time = da_crop.expand_dims(dim={'time': [dt64]})

    da_list.append(da_time)
    
# combine dataarrays into one
da_full = xr.concat(da_list, dim='time')

# merge data with grid dataset
ds_merged = xr.merge([grid_ds, da_full]).set_coords(('latitude', 'longitude'))

# get rid of negative (NaN) values
ds_merged = ds_merged.where(ds_merged['rain'] >= 0.)

# rename
ds_rename = ds_merged.rename({'lines': 'x', 'elems': 'y', 'latitude': 'lat', 'longitude': 'lon'})

# resample to hourly
ds_resample = ds_rename.resample(time='1H', label='right').mean()

# save data as a netCDF
he_da = ds_resample.rain
he_da.to_netcdf(save_path)