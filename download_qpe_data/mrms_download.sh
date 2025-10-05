#!/bin/bash
  
# set dates for download
year=2021        # year of desired data 
month_start=1    # beginning month of desired data 
month_end=1      # end month of desired data 
day_start=27     # beginning day of desired data 
day_end=30       # end day of desired data 

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


'''
# ---------------------------------------------------------------------------------------------------------
# OPTIONAL: unzip gz files

# loop over files and unzip
for file in "$directory"/*; do
    gunzip $file
done
# ---------------------------------------------------------------------------------------------------------
'''


'''
# ---------------------------------------------------------------------------------------------------------
# OPTIONAL: convert grib2 to netcdf (requires NCO)

# loop over files and convert to netcdf
for file in "$directory"/*.grib2; do
    ncl_convert2nc $file -itime -o $directory
done
# ---------------------------------------------------------------------------------------------------------
'''



'''
# ---------------------------------------------------------------------------------------------------------
# OPTIONAL: loop over files and crop to desired lat/lon domain (requires NCO)

# define domain bounds
lat_lower=32.
lat_upper=38.
lon_lower=237.
lon_upper=246.

# make directory for cropped data 
end_directory="./mrms_cropped_ncs"
mkdir -p "$end_directory"

for file in "$directory"/*.grib2; do
    ncl_convert2nc $file -itime -o $directory
done


# loop over files and crop
for file in "$directory"/*.nc; do

    extension="${file##*.}"
    filename=$(basename "$file" ".$extension")
    new_filename="${filename}_cropped.${extension}"

    new_filepath="$end_directory/$new_filename"

    ncea -d lon_0,${lon_lower},${lon_upper} -d lat_0,${lat_lower},${lat_upper} $file $new_filepath
done
# ---------------------------------------------------------------------------------------------------------
'''