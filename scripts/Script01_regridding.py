## Python script for Regridding the data (to be run following Script00.py)
### This is a python script for regridding the data. Here we use the xesmf module to regrid.
### Since this is precipitation, we use conservative regridding method. 
### The input files include the netcdf files for each year of the high resolution dataset
### Additionally, the regridder can be reused by saving the weights. For this run the script for a shorter period.
### Save the regridder in netcdf format so that it can be reused. A new regridder should be developed for different resolution and regridding algorithm.
### The output is a series of netcdf files corresponding to each year at a lower resolution compared to input files.
import xarray as xr
import numpy as np
import xesmf as xe


#### Change the weights file before running for other resolutions
fn=xr.open_dataset('/regrid_weights/conservative_1800x3600_180x360.nc') ### Reading in the weights that has been saved
datadir = '/level01_indata/' ## Use the preprocessed raw data output from Script00.py here
in_res = 10  ## spatial resolution of input dataset in kilometers (10km for IMERG; 100 km for FROGS)
out_res = 100 ## spatial resolution of output dataset in kilometers
out_res_deg = out_res/100 ## spatial resolution of output dataset in degrees (considering 1 degree is approximately 100km)

for yr in np.arange(1998,2025): ### Looping over each year
    data1= xr.open_dataset(datadir+str(yr)+'.nc') ## Reading in the data
    ### Extracting the lat-lon bounds for the existing dataset to construct the output grid
    lnmx=max(data1.lon.values); lnmn = min(data1.lon.values)
    ltmx=max(data1.lat.values); ltmn = min(data1.lat.values)

    ### Need to apply conditions to extract the bounds based on which hemisphere the bounds are in.
    if lnmn<0:
        rlnmn=round(lnmn)+(out_res_deg/2)
    else:
        rlnmn=round(lnmn)-(out_res_deg/2)
    if ltmn<0:
        rltmn=round(ltmn)+(out_res_deg/2)
    else:
        rltmn=round(ltmn)-(out_res_deg/2)
    if lnmx<0:
        rlnmx = round(lnmx)+(out_res_deg/2)
    else:
        rlnmx = round(lnmx)-(out_res_deg/2)
    if ltmx<0:
        rltmx = round(ltmx)+(out_res_deg/2)
    else:
        rltmx = round(ltmx)-(out_res_deg/2)
    lon_count = int((len(data1.lon.values))/(out_res/in_res))
    lat_count = int((len(data1.lat.values))/(out_res/in_res))
    ### Next we set up the grid of the output
    outgrid = {'lon': np.linspace(rlnmn, rlnmx, lon_count),
                            'lat': np.linspace(rltmn, rltmx, lat_count),
                            'lon_b': np.linspace(round(lnmn), round(lnmx), lon_count+1),
                            'lat_b': np.linspace(round(ltmn), round(ltmx), lat_count+1).clip(round(ltmn), round(ltmx)),
                            } 
    print ('regridding')
    regridder = xe.Regridder(data1, outgrid, 'conservative',periodic=True,weights=fn) ### Consructing regridder
    #fn = regridder.to_netcdf() ### Saving the regridder once it has been constructed. Only need to be used for a new resolution.
    data2=regridder(data1) ### Regridding the input data
    del data1
    print ('regridded')
    comp = dict(zlib=True, complevel=5)
    encoding = {var: comp for var in data2.data_vars}
    filename_km = '/level01_indata/imerg_'+str(out_res)+'km/'+str(yr)+'.nc' ### output location
    print ('saving to ', filename_km)
    data2.to_netcdf(path=filename_km,encoding=encoding) ### Saving output
    data2.close()
    print ("saved", yr)
print ('finished saving '+str(out_res)+'km')

