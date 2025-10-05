#!/bin/bash
  
  
# set dates for download
year=2021        # year of desired data 
month_start=1    # beginning month of desired data 
month_end=1      # end month of desired data 
day_start=27     # beginning day of desired data 
day_end=30       # end day of desired data 

# make directory for data 
directory="./he_files"  
grid_directory="./he_grid_file"

mkdir -p "$directory"
mkdir -p "$grid_directory"

# download grid file
wget -P "$grid_directory" "https://noaa-ghe-pds.s3.amazonaws.com/NPR.GEO.GHE.v1.Navigation.netcdf.gz"

# define base url to download from 
base_url="https://noaa-ghe-pds.s3.amazonaws.com/rain_rate/${year}"

# loop over days, hours, and minutes
for ((month=$month_start; month<=$month_end; month++)); do
    month_with_zero=$(printf "%02d" $month)

    for ((day=$day_start; day<=$day_end; day++)); do
        day_with_zero=$(printf "%02d" $day)

        for ((number=0; number<=23; number++)); do
            number_with_zero=$(printf "%02d" $number)

            for minute in 00 15 30 45; do
            
                # define location of netcdf file for each 1/4 hour
                url="${base_url}/${month_with_zero}/${day_with_zero}/NPR.GEO.GHE.v1.S\
                ${year}${month_with_zero}${day_with_zero}${hour_with_zero}${minute}.nc.gz"
                
                # download file for each 1/4 hour
                wget -P "$directory" "$url"

           done
        done
    done
done


'''
# ---------------------------------------------------------------------------------------------------------
# OPTIONAL: unzip gz files

# loop over files and unzip
for file in "$directory"/*; do
    gunzip $file
done
# ---------------------------------------------------------------------------------------------------------
'''