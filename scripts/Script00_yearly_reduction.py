## Script for merging and reducing size (to be run first following download of data)
## IMERG data is available as netcdf files for one file per day (for the daily product)
### This is the script to merge and reduce the size of the dataset. 
### The script takes the raw netcdf files (from IMERG) and merges them based on each year.
### The input is raw netcdf files and the output is the netcdf files for each year.
import xarray as xr
import numpy as np
from glob import glob

print ('Starting')
datadir='/input_data_directory/'
for yr in np.arange(2000,2024): ### Looping through all the years of data in the folder
    fname=glob(datadir+'*'+str(yr)+'*')
    HR= xr.open_mfdataset(fname)
    print (str(yr)+' imported')
    HR=HR.precipitation.sel(time=str(yr)) ### Here we select all the netcdf files based on the year.
    print ('Loading')
    HR.load() ### Loading to remove chunking of data
    print ('processed')
    filename_out = '/output_data_directory/'+str(yr)+'.nc' ## output location
    print ('saving to ', filename_out)
    HR.to_netcdf(path=filename_out) ### Saving output
    HR.close()
    print ("saved", yr)
print ('finished saving nc file')
