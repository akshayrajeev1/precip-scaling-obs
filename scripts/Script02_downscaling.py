## Script for regridding upscaling data (to be executed following Script01)
### This is to bring back the low resolution data to high-resolution using nearest regridding method.
### It is required for the calculation of joint rain amount distribution (using like histogram)
### For this the inputs are the high-res and low-res versions of the data.
### The output is essentially a high resolution version of the low resolution dataset.
import xarray as xr
import numpy as np
import xesmf as xe
print ('Starting')

for yr in np.arange(2000,2023): ### Looping over each year
    HR= xr.open_dataset('/gpm_10km/'+str(yr)+'.nc')  ## Reading in the raw data output from Scrip00 (high-res)
    LR = xr.open_dataset('/gpm_100km/'+str(yr)+'.nc')  ## Reading in the Low-res data
    print ('Data input done for ', str(yr))  
    regridder = xe.Regridder(LR, HR, 'nearest_s2d')
    LRh = regridder(LR)
    print ('Regridding done')
    comp = dict(zlib=True, complevel=5)
    encoding = {var: comp for var in LRh.data_vars}
    filename_LRh = '/share/cliprelabs/ar942/GPM/gpm_nearest/gpm_100km/'+str(yr)+'.nc' ### Output location
    print ('saving to ', filename_LRh)
    LRh.to_netcdf(path=filename_LRh,encoding=encoding) ### Saving output
    LRh.close()
    print ("saved", yr)
print ('finished saving nc file')
