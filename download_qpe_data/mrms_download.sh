#!/bin/bash
  
# set dates for download
year=2025        # USER INPUT! year of desired data 
month_start=2    # USER INPUT! beginning month of desired data 
month_end=2      # USER INPUT! end month of desired data 
day_start=12     # USER INPUT! beginning day of desired data 
day_end=15       # USER INPUT! end day of desired data 

# make directory for data 
directory="./mrms_ncs"    

mkdir -p "$directory"

# define base url to download from 
base_url="https://mtarchive.geol.iastate.edu/${year}/"

# loop over days and hours
for ((month=$month_start; month<=$month_end; month++)); do
    month_with_zero=$(printf "%02d" $month)

    for ((day=$day_start; day<=$day_end; day++)); do
        day_with_zero=$(printf "%02d" $day)

        for ((number=0; number<=23; number++)); do
            number_with_zero=$(printf "%02d" $number)

            # define location of file for each hour
            url="${base_url}${month_with_zero}/${day_with_zero}/mrms/ncep/MultiSensor_QPE_01H_Pass2\
/MultiSensor_QPE_01H_Pass2_00.00_${year}${month_with_zero}${day_with_zero}-${number_with_zero}0000.grib2.gz"
            
            # download file for each hour
            wget -P "$directory" "$url"
        done
    done
done



# ---------------------------------------------------------------------------------------------------------
# OPTIONAL: unzip gz files

# loop over files and unzip
for file in "$directory"/*; do
    gunzip $file
done
# ---------------------------------------------------------------------------------------------------------




# ---------------------------------------------------------------------------------------------------------
# OPTIONAL: convert grib2 to netcdf (requires NCO)

# loop over files and convert to netcdf
for file in "$directory"/*.grib2; do
    ncl_convert2nc $file -itime -o $directory
done
# ---------------------------------------------------------------------------------------------------------


