#!/bin/bash
  
  
# set dates for download
year=2021        # year of desired data 
month_start=1    # beginning month of desired data 
month_end=1      # end month of desired data 
day_start=27     # beginning day of desired data 
day_end=30       # end day of desired data 

# make directory for data 
directory="./cmorph_files"    
mkdir -p "$directory"

# define base url to download from 
base_url="https://www.ncei.noaa.gov/data/cmorph-high-resolution-global-precipitation-estimates/access/30min/8km/${year}"

# loop over days and hours
for ((month=$month_start; month<=$month_end; month++)); do
    month_with_zero=$(printf "%02d" $month)

    for ((day=$day_start; day<=$day_end; day++)); do
        day_with_zero=$(printf "%02d" $day)

        for ((number=0; number<=23; number++)); do
            number_with_zero=$(printf "%02d" $number)

            # define location of file for each hour
            url="${base_url}/${month_with_zero}/${day_with_zero}/CMORPH_V1.0_ADJ_8km-30min_${year}${month_with_zero}${day_with_zero}${number_with_zero}.nc"
            
            # download file for each hour
            wget -P "$directory" "$url"
        done
    done
done


'''
# ---------------------------------------------------------------------------------------------------------
# OPTIONAL: loop over files and crop to desired lat/lon domain (requires NCO)

# define domain bounds
lat_lower=32.
lat_upper=38.
lon_lower=237.
lon_upper=246.

# make directory for cropped data 
end_directory="./cmorph_cropped_files"
mkdir -p "$end_directory"

# loop over files and crop
for file in "$directory"/*.nc; do

    extension="${file##*.}"
    filename=$(basename "$file" ".$extension")
    new_filename="${filename}_cropped.${extension}"

    new_filepath="$end_directory/$new_filename"

    ncea -d lon,${lon_lower},${lon_upper} -d lat,${lat_lower},${lat_upper} $file $new_filepath
done
# ---------------------------------------------------------------------------------------------------------
'''