## Script for merging individual netcdf to annual files (to be run first following download of data)
## IMERG data is available as netcdf files for one file per day (for the daily product)
### This is the script to merge the dataset making it easier to manage. 
### The script takes the raw netcdf files (from IMERG) and merges them based on each year.
### The input is raw netcdf files and the output is the netcdf files for each year.
import xarray as xr
import numpy as np
from glob import glob

print ('Starting')
datadir='/level00_indata/' ### Here level-0 is the raw data that was downloaded from the source.
for yr in np.arange(1998,2025): ### Looping through all the years of data in the folder
    fname=glob(datadir+'*'+str(yr)+'*')
    HR= xr.open_mfdataset(fname)
    print (str(yr)+' imported')
    HR=HR.precipitation.sel(time=str(yr)) ### Here we select all the netcdf files based on the year.
    print ('Loading')
    HR.load() ### Loading to remove chunking of data
    print ('processed')
    filename_out = '/level01_indata/'+str(yr)+'.nc' ### Here level-1 is the merged data
    print ('saving to ', filename_out)
    HR.to_netcdf(path=filename_out) ### Saving output
    HR.close()
    print ("saved", yr)
print ('finished saving nc file')
