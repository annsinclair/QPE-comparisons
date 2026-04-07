#!/usr/bin/env python
"""
Filename: mrmsro_clean.py
Author: Ann Sinclair
Date: 2026-04-07
Version: 1.0
Description: Clean downloaded MRMS Radar-Only files and save as netCDF files
"""

# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
# USER INPUT! location of downloaded data
file_path = 'path/to/mrmsro_files'
# USER INPUT! location to store cleaned data
save_path = '/path/to/store/cleaned_data/mrmsro.nc'

# open downloaded data files as one dataset
files = glob.glob(os.path.join(file_path, "*.nc"))
ds = xr.open_mfdataset(files, combine='by_coords')
print('data successfully imported')

# select just the precip variable
mrmsro_da = ds.RadarOnlyQPE01H_P0_L102_GLL0

# rename variables
mrmsro_da = mrmsro_da.rename(
    {'initial_time0_hours': 'time', 'lat_0': 'lat', 'lon_0': 'lon'})

# change from 360 lon to +/- 180
mrmsro_da = mrmsro_da.assign_coords(lon=(mrmsro_da.lon - 360))

# save data as a netCDF
mrmsro_da.to_netcdf(save_path)
print('netCDF saved to', save_path)
