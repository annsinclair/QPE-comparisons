# import libraries

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import sys
import os
import datetime

def time_elapsed(datetimes):
    """Calculate the time elapsed between gauge readings.

    datetimes: list of datetimes corresponding to gauge readings

    Returns:
    df (pandas DataFrame): dataframe with original times and elapsed times

    """
    
    # set up dataframe
    datetime_series = pd.Series(datetimes)
    datetime_series = pd.to_datetime(datetime_series)
    
    # calculate time between readings
    time_elapsed_s = datetime_series.diff().dt.total_seconds()      # calculate time elapsed in seconds
    time_elapsed_h = time_elapsed_s / 3600                          # convert to time elapsed in hours
    df = pd.DataFrame(data={'time_elapsed': time_elapsed_h, 'date_time': datetimes})
    df['date_time'] = pd.to_datetime(df['date_time'])
    df = df.set_index('date_time')
    
    return df


def resample(data_raw, datetimes):
    """Resample gauge data to hourly intensities. 

    data_raw: list of rain gauge measurements (intensities, not cumulative)
    datetimes: list of datetimes corresponding to gauge readings

    Returns:
    precip_resample (pandas Series): resampled hourly gauge data

    """
    
    # set up dataframe
    df = pd.DataFrame(data={'precip_data': data_raw, 'date_time': datetimes})
    df['date_time'] = pd.to_datetime(df['date_time'])
    df = df.set_index('date_time')
    df = df.set_index(df.index.tz_localize(None))
    df = df.dropna(subset=['precip_data'])
    df = df.join(time_elapsed(df.index.values).tz_localize(None))

    precip = df['precip_data'].copy().dropna()
    indices = precip.index

    # resample precip data to hourly temporal resolution    
    for i in range(len(indices))[1:]:                               # loop through all indices      
        if (df['time_elapsed'].loc[indices[i]] > 1):                # find intervals of >1 hour
            if precip.loc[indices[i]] != 0:                         # check if there is precip recorded during the interval

                indices_new = precip.index
                i_new = np.where(indices_new.values == indices[i])[0][0]
                # we assume constant precip intensity during >hourly period (this is conservative)
                # first, break the >hourly period into 5 minute intervals
                time_jump = precip.iloc[i_new-1:i_new+1]
                temp_col = time_jump.resample('5T', origin='start').sum()
                # divide the original amount recorded by the number of new 5 min periods
                old_value = temp_col.iloc[-1]
                count = len(temp_col[1:])
                value_dist = old_value / count
                # populate temporary column with even precip intensities that sum to original recorded amount
                temp_col.iloc[1:] = value_dist

                # place the new 5 minute rainfall intervals into the precipitation time series
                if indices[i] == indices[-1]:
                    precip = pd.concat((precip.loc[:indices_new[i_new-1]], temp_col[1:]))
                else:
                    precip = pd.concat((precip.loc[:indices_new[i_new-1]], temp_col[1:], precip.loc[indices_new[i_new+1]:]))

    # resample rainfall data to hourly intervals
    # this will sum data recorded at subhourly intervals
    # the process above ensures that >hourly intervals are handled currectly
    precip_resample = precip.cumsum().resample('1H').ffill().diff().fillna(0)
    
    return precip_resample


def get_atlas14(which='mean', folderpath=None):
    """Get path to folder with specified Atlas 14 data.  

    which (string): 'mean', 'upper', or 'lower' - type of intensity data to get
    folderpath (None or string): when given, the path to Atlas 14 data. 
        If not given, Atlas 14 data is assumed to be in a folder ./atlas14_files/
        in the same location as file.

    Returns:
    atlas14_root (Path): path to specified Atlas 14 data

    """
    
    if folderpath == None:
        cur_path = os.path.dirname(__file__)
        atlas14_path = os.path.join(cur_path, 'atlas14_files')
        
    else:
        atlas14_path = folderpath
    
    if which == 'mean':
        atlas14_root = os.path.join(atlas14_path, 'atlas14_pds_mean')
        
    elif which == 'upper':
        atlas14_root = os.path.join(atlas14_path, 'atlas14_pds_upper')
        
    elif which == 'lower':
        atlas14_root = os.path.join(atlas14_path, 'atlas14_pds_lower')
        
    else:
        raise KeyWordError("'which' keyword must be one of 'upper', 'lower', or 'mean'")
    
    return atlas14_root

def get_atlas14_durations():
    """Dictionary with Atlas 14 durations and labels for calling data."""
    
    atlas14_durations = {'5m' : [5/60, '05m'], 
                         '10m': [10/60, '10m'], 
                         '15m': [15/60, '15m'],
                         '30m': [30/60, '30m'], 
                         '60m': [1, '60m'], 
                         '2h' : [2, '02h'],
                         '3h' : [3, '03h'], 
                         '6h' : [6, '06h'], 
                         '12h': [12, '12h'], 
                         '24h': [24, '24h'],
                         '2d' : [2*24, '48h'], 
                         '3d' : [3*24, '03d'], 
                         '4d' : [4*24, '04d']}
    
    return atlas14_durations


def quality_control(data, datetimes, PFDS=True, PFDS_folder=None, lat=None, lon=None, plot=True):
    """Quality control gauge data

    data: list of rain gauge measurements (intensities, not cumulative)
    datetimes: list of datetimes corresponding to gauge readings
    PFDS (bool, default True): whether or not to use the Atlas 14 precipitation frequency data server 
        to calculate likely non-physical rain
    PFDS_folder (None or string, default None): path to Atlas 14 data. 
        If not given, Atlas 14 data is assumed to be in a folder ./atlas14_files/
        in the same location as file.
    lat (float): latitude of rain gauge in degrees
    lon (float): longitude of rain gauge in degrees (-180 to 180)
    plot (bool, default True): whether to plot data if it fails to pass QC

    Returns:
    qc_flag (string): 'pass' if gauge data passes quality control,
        if not, describes why the gauge failed quality control
    """
    
    qc_flags = {
        0: 'pass', 
        1: 'not hourly', 
        2: 'negative readings', 
        3: 'intensity greater than 1000 year retun interval',
        4: 'isolated high intensity',
        5: 'accumulation greater than 1000 year return interval'
    }

    # set up dataframe
    df = pd.DataFrame(data={'precip_data': data, 'date_time': datetimes})
    df['date_time'] = pd.to_datetime(df['date_time'])
    df = df.set_index('date_time')
    df = df.join(time_elapsed(datetimes))
    
    qc_flag = 0
    
    #test if readings have hourly/subhourly temporal resolution
    if (df['time_elapsed'].dropna() > 1).all() == True:
        if (df['precip_data'].dropna() == 0).all() == False:
            qc_flag = 1                                             # station fails QC if readings are longer than hourly
            
    # define data, copies, and indices
    precip = df['precip_data']
    precip_orig = precip.copy()                                     # copy of original data    
    
    # set up precip observations to use for QC process    
    precip_qc = precip.copy().dropna()                              # copy of original data without NaNs
    indices = precip_qc.index                                       # times associated with gauge readings
    
    precip_qc_copy = precip_qc.copy()                               # copy of qc data
    precip_qc_sum = precip_qc_copy.cumsum()                         # accumulated precip data
    precip_qc_sum_resample = precip_qc_sum.resample('1H').ffill()   # accumulated data resampled to hourly
    precip_qc_resample = precip_qc_sum_resample.diff().fillna(0)    # interval data at hourly resolution
    
    # check for "negative" rainfall values
    if (precip_orig < 0).any() == True:
        qc_flag = 2                                               

    # check for unrealistic spikes in rainfall data
    if PFDS == True:
        atlas14_durations = get_atlas14_durations()
        
        atlas14_root_mean = get_atlas14(which='mean', folderpath=PFDS_folder)
        atlas14_root_upper = get_atlas14(which='upper', folderpath=PFDS_folder)

        
        # loop through each gauge reading
        for i in range(len(indices))[1:]:
            rainspike = precip_qc[indices[i]]
            # find length of time between last reading and current reading
            spike_duration = df['time_elapsed'][indices[i]] 
            # find the atlas 14 duration that best matches the duration of the reading
            duration_key = min(atlas14_durations.items(), key=lambda x: abs(spike_duration - x[1][0]))

            # find the 1000 year return interval intensity associated with the duration
            atlas14_path = f'{atlas14_root_mean}/{duration_key[0]}_pds/sw1000yr{duration_key[1][1]}a.nc'
            atlas14_da = xr.open_dataarray(atlas14_path)
            atlas14_int = atlas14_da.sel(lat=lat, lon=lon, method='nearest').values[0]

            # find the upper confidence interval of 1000 year return interval intensity associated with the duration
            atlas14_path_upper = f'{atlas14_root_upper}/{duration_key[0]}_pds/sw1000yr{duration_key[1][1]}au.nc'
            atlas14_da_upper = xr.open_dataarray(atlas14_path_upper)
            atlas14_int_upper = atlas14_da_upper.sel(lat=lat, lon=lon, method='nearest').values[0]

            # check if intensity is greater than 1.5x the upper level of 1000 return interval intensity 
            if rainspike > 1.5*atlas14_int_upper:
                qc_flag = 3                                         
                break

            # check if intensity recorded rainfall is isolated (ie., no precip leading up to or following) 
            elif rainspike > atlas14_int:
                # search 5 readings before and 5 readings after
                # station is flagged if the readings either before or after are less than 0.1x the recorded high intensity
                cond_pre = (precip_qc[indices[i-5:i]] < (0.1 * rainspike)).all()
                cond_post = (precip_qc[indices[i+1:i+6]] < (0.1 * rainspike)).all()
                if (cond_pre == True) | (cond_post == True):
                    qc_flag = 4                                     
                    break

        # check for unrealistically high accumulation values
        if qc_flag == 0:
            # loop over all atlas 14 durations greater than 1 hour
            for key in list(atlas14_durations.keys())[4:]:
                # generate rolling sums of precipitation for each duration
                time_sum = precip_qc_resample.rolling(atlas14_durations[key][0]).sum().max()
                # find the upper confidence interval of 1000 year return interval intensity associated with the duration
                atlas14_path_upper = f'{atlas14_root_upper}/{key}_pds/sw1000yr{atlas14_durations[key][1]}au.nc'
                atlas14_da_upper = xr.open_dataarray(atlas14_path_upper)
                atlas14_int_upper = atlas14_da_upper.sel(lat=lat, lon=lon, method='nearest').values[0]

                # check if intensity is greater than 1.5x the upper level of 1000 return interval intensity 
                if time_sum > (1.5*atlas14_int_upper):
                    qc_flag = 5.                                       
                    break
                
    if plot == True:
        if qc_flag == 0:
            print('QC passed, flag = 0')
        if qc_flag != 0:
            print(f'QC fail with flag: {qc_flag} - {qc_flags[qc_flag]}')
            precip_orig.fillna(0).plot()
            plt.show()
    
    return qc_flag
                  
                  
    