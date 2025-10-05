#!/bin/bash
  
  
# set dates for download
year=2021        # year of desired data 
month_start=1    # beginning month of desired data 
month_end=1      # end month of desired data 
day_start=27     # beginning day of desired data 
day_end=30       # end day of desired data 

# make directory for data 
directory="./gsmap_files"
mkdir -p "$directory"

# loop over days
for ((month=$month_start; month<=$month_end; month++)); do
    month_with_zero=$(printf "%02d" $month)

    for ((day=$day_start; day<=$day_end; day++)); do
        day_with_zero=$(printf "%02d" $day)

        # define location of netcdf file for each hour
        url="${HOST}/standard/v8/hourly_G/${year}/${month_with_zero}/${day_with_zero}/*"
        
        # download file for all hours of each day
        wget --ftp-user="$USER" --ftp-password="$PASSWORD" --directory-prefix="$directory" -r -nH --cut-dirs=6 "$url"

        done
    done
done
