#!/bin/bash
  
  
# set dates for download
year=2025        # USER INPUT! year of desired data 
month_start=2    # USER INPUT! beginning month of desired data 
month_end=2      # USER INPUT! end month of desired data 
day_start=12     # USER INPUT! beginning day of desired data 
day_end=15       # USER INPUT! end day of desired data  

# set forecast hour 
fh=1            
prev_day=$((day_start-1))
prev_hour=$((24-fh))
final_hour=$((23-fh))

# make directory for data 
directory="./hrrr_files"    
mkdir -p "$directory"

# define base url to download from 
base_url="https://storage.googleapis.com/high-resolution-rapid-refresh/hrrr.${year}"

# loop over days and hours
for ((month=$month_start; month<=$month_end; month++)); do
    month_with_zero=$(printf "%02d" $month)

    for ((day=$prev_day; day<=$day_end; day++)); do
        day_with_zero=$(printf "%02d" $day)

        if [[ $day -eq $prev_day ]]; then
            start_number=$prev_hour
            end_number=23

        elif [[ $day -eq $day_end ]]; then
            start_number=0
            end_number=$final_hour

        else
            start_number=0
            end_number=23

        fi

        for ((number=$start_number; number<=$end_number; number++)); do
            number_with_zero=$(printf "%02d" $number)

            # define location of file for each hour
            url="${base_url}${month_with_zero}${day_with_zero}/conus/hrrr.t${number_with_zero}z.wrfsfcf01.grib2"
            fname="$directory/${year}${month_with_zero}${day_with_zero}_${number_with_zero}_f0${fh}.grib2"
            
            # download file for each hour
            wget -O "$fname" "$url"
            
        done
    done
done



# ---------------------------------------------------------------------------------------------------------
# OPTIONAL: convert from grib2 to netcdf (requires NCL)

# loop over files and convert
for file in "$directory"/*; do
    ncl_convert2nc $file -itime -o "$directory"
done

# ---------------------------------------------------------------------------------------------------------
