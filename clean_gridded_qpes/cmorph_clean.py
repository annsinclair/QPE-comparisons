# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = 'path/to/cmorph_files'                  # USER INPUT! location of downloaded data
save_path = '/path/to/store/cleaned_data/cmorph.nc' # USER INPUT! location to store cleaned data

# open downloaded data files as one dataset
files = glob.glob(os.path.join(file_path, "*.nc"))
ds = xr.open_mfdataset(files, combine='by_coords')
print('data successfully imported')

# resample to hourly data
ds_resample = ds.resample(time='1H', label='right').mean()
print('data resampled to hourly')

# select just the precip variable
cmorph_da = ds_resample.cmorph

# change from 360 lon to +/- 180
cmorph_da = cmorph_da.assign_coords(lon=(cmorph_da.lon - 360))

# get rid of negative values (CMORPH uses -9999 for NaN values)
cmorph_da = cmorph_da.where(cmorph_da_new >= 0.)

# save data as a netCDF
cmorph_da.to_netcdf(save_path)
print('netCDF saved to', save_path)