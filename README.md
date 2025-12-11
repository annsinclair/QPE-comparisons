# QPE-comparisons
## Code for downloading, cleaning, and comparing gridded QPE products

This repository contains code for downloading 12 gridded QPE products, downloading and performing quality control on gauges from the Synoptic Data Weather API, and comparing precipitation estimates over a region as well as at the site of a specific event. 

The organization of the respository is as follows:

### gauge_data
The gauge_data folder contains a file (resample_qc.py) with functions for performing quality control on gauge data and for resampling gauge readings into hourly intensities. Examples of downloading gauge data from the Synoptic Weather API and using the resample_qc.py functions is provided as well (synoptic_download_qc.ipynb)

### download_qpe_data
This folder contains a collection of files with instructions for downloading gridded QPE products. .sh files are bash scripts that use wget to download QPE data, while .txt files are instructions for downloading products that are not available online through wget. 

### clean_gridded_qpes
The clean_gridded_qpes folder contains python files for organizing the downloaded QPE data into one generalized format, making it easier to work with for the comparison code. 

### comparison_notebooks
This folder contains two jupyter notebooks with code for comparing gridded QPE products to one another and to gauge data. spatial_comparisons.ipynb is for looking at the differences in precipitation over a region as reported by different QPEs. ls_comparison.ipynb has code for looking at precipitation time series at a specific location. 

