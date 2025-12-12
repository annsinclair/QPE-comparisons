# import libraries
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = '/projects/b1045/asinclair/ARs/feb2025/gsmap/gsmap_files'                  # USER INPUT! location of downloaded data
save_path = '/projects/b1045/asinclair/ARs/feb2025/qpe_datasets/gsmap.nc' # USER INPUT! location to store cleaned data

crop = True                                         # USER INPUT! True or False (to crop or not to crop...)

if crop == True:
    # define bounds of study area, if desired 
    lon_min = -123                                  # USER INPUT! longitude bound 1 (from -180-180)
    lon_max = -114                                  # USER INPUT! longitude bound 2 (from -180-180)
    lat_min = 32                                    # USER INPUT! latitude bound 1 
    lat_max = 38                                    # USER INPUT! latitude bound 2

# import files 
files = sorted(glob.glob(os.path.join(file_path, "*.nc")))

# define list for indivual hour data
da_list = []

# loop through hourly files, clean, add time coordinate
for file in files:
    # open dataset
    ds = xr.open_dataset(file)

    # get datetime from dataset attributes
    attr_list = ds.attrs['FileHeader'].split(';\n')
    for attr in attr_list:
        if 'StartGranuleDateTime' in attr:
            time_str = attr
    dt_str = time_str.split('=')[1][:-1]
    dt = np.datetime64(dt_str)
    
    # define lat and lon values
    lat_flat = ds.Latitude.values[0]
    lon_flat = ds.Longitude.values.T[0]

    # define/re-define time, lat, and lon coordinates
    ds = ds.assign_coords({'lat':('nlat', lat_flat), 'lon':('nlon', lon_flat), 'time':dt})
    ds = ds.drop_vars(['Latitude', 'Longitude'])
    ds = ds.rename({'nlon':'lon', 'nlat':'lat'})

    # get the hourly precip data
    da = ds.hourlyPrecipRateGC

    # crop to study area
    if crop == True:
        da = da.where(
            ((da.lat>=lat_min) & (da.lat<=lat_max)) & 
            ((da.lon>=lon_min) & (da.lon<=lon_max)), drop=True
        )

    da_list.append(da)
print('files imported and cleaned')

# combine hourly data to one dataarray
da_full = xr.concat(da_list, dim='time')
print('files combined')

# add an hour to time to make hour labels consistent with other products
da_full['time'] = da_full['time'] + np.timedelta64(1, 'h')

# transpose variables to match with other products (this makes things easier later)
da_full = da_full.transpose('time', 'lat', 'lon')

# save data as a netCDF
da_full.to_netcdf(save_path)
print('netCDF saved to', save_path)