# import libraries
import gzip
import numpy as np
import xarray as xr
import glob
import os

# define paths
file_path = 'path/to/gsmap_files'                  # USER INPUT! location of downloaded data
save_path = '/path/to/store/cleaned_data/gsmap.nc' # USER INPUT! location to store cleaned data

# define beginning and end dates of files 
begin_time = '2021-01-27T00:00'                    # USER INPUT! time of first file
end_time = '2021-01-31T00:00'                      # USER INPUT! time of last file

# define bounds of study area, if desired 
lon_min = 237                                      # USER INPUT! longitude bound 1 (from 0-360)
lon_max = 246                                      # USER INPUT! longitude bound 2 (from 0-360)
lat_min = 32                                       # USER INPUT! latitude bound 1 
lat_max = 38                                       # USER INPUT! latitude bound 2

if len(time_array) != len(files):
    print('warning! number of files is not the same as number of times defined. this will cause problems later on')

# define gloabl grid
lon = np.linspace(0.05, 359.95, 3600)
lat = np.linspace(59.95, -59.95, 1200)

# create masks to crop to study area
mask_lon = (lon_min <= lon) & (lon <= lon_max)
mask_lat = (lat_min <= lat) & (lat <= lat_max)
lon_crop = lon[mask_lon]
lat_crop = lat[mask_lat]

# unzip and reshape .gz files
array_list = []
for file in sorted(files):
    unzipped = gzip.GzipFile(file, 'rb')
    data_1d = np.frombuffer(unzipped.read(), dtype=np.float32)
    data = data_1d.reshape((1200, 3600))
    data_crop = data[mask_lat, :][:, mask_lon]
    array_list.append(data_crop)

# stack arrays
array_3d = np.dstack(array_list)

# define hourly array of times (should match # of files)
time_array = np.arange(begin_time, end_time, dtype='datetime64[h]')

# create dataarray object
gsmap_da = xr.DataArray(
    data=array_3d,
    dims=['lat', 'lon', 'time'],
    coords=dict(
        lon=(lon_crop),
        lat=(lat_crop),
        time=(time_array + np.timedelta64(1, 'h'))
    ),)

# change from 360 lon to +/- 180
gsmap_da = gsmap_da.assign_coords(lon=(gsmap_da.lon - 360))

# save data as a netCDF
gsmap_da.to_netcdf(save_path)
print('netCDF saved to', save_path)