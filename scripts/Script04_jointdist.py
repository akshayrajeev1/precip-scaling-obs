### This is the script for estimating the joint distribution of rain amounts at high and low resolutions.
### This script should be executed following Script03. It can also be executed following Script02 since all required inputs 
### should already be available. The basic logic behind the script is to loop through the rain rates at HR and LR
### and for each grid which satisify those rain rate conditions, find the rain amount in 1) LR dataset and 2) HR dataset.
### The input for this script is the HR dataset and the downscaled (Script02) LR dataset.
### The output should be a plot showing the joint distribution of rain amounts at HR and LR.

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import rioxarray
from xhistogram.xarray import histogram
from dask.distributed import LocalCluster, Client
import dask

lr_list=[25,100,200,500,1000]

# Set temp dir for Dask
dask.config.set(temporary_directory='/tmp')
cluster = LocalCluster(n_workers=4, threads_per_worker=1, memory_limit='25GB')
client = Client(cluster)
print("Dashboard:", client.dashboard_link, flush=True)
def makejointdist(HR,LR):
    L=2.5e6
    ndmat=len(HR.time)
    maxp=1500;# % choose an arbitrary upper bound for initial distribution, in w/m2
    minp=1;# % arbitrary lower bound, in w/m2. Make sure to set this low enough that you catch most of the rain. 
        #%%% thoughts: it might be better to specify the minimum threshold and the                                     
        #%%% bin spacing, which I have around 7%. The goals are to capture as much                                     
        #%%% of the distribution as possible and to balance sampling against                                           
        #%%% resolution. Capturing the upper end is easy: just extend the bins to                                      
        #%%% include the heaviest precipitation event in the dataset. The lower end                                    
        #%%% is harder: it can go all the way to machine epsilon, and there is no                                       
        #%%% obvious reasonable threshold for "rain" over a large spatial scale. The                                   
        #%%% value I chose here captures 97% of rainfall in CMIP5.                                                     
    nbins=100;
    binrlog=np.linspace(np.log(minp),np.log(maxp),nbins);
    dbinlog=np.diff(binrlog);
    binllog=binrlog-dbinlog[0];
    binr=np.exp(binrlog)/L*3600*24;
    binl=np.exp(binllog)/L*3600*24;
    dbin=dbinlog[0];
    binrlogex=binrlog;
    binrend=np.exp(binrlogex[len(binrlogex)-1])
        #% extend the bins until the maximum precip anywhere in the dataset falls
        #% within the bins
        # switch maxp to pmax if you want it to depend on your data
    while maxp>binr[len(binr)-1]:
        binrlogex=np.append(binrlogex,binrlogex[len(binrlogex)-1]+dbin)
        binrend=np.exp(binrlogex[len(binrlogex)-1]);
        binrlog=binrlogex;
        binllog=binrlog-dbinlog[0];
        binl=np.exp(binllog)/L*3600*24; #%% this is what we'll use to make distributions
        binr=np.exp(binrlog)/L*3600*24;
    bincrates=np.append(0,(binl+binr)/2)# % we'll use this for plotting.
    #print("bincrates done")
    bins=np.append(0,binl)
    LR_bins=bins
    HR_bins=bins
    db=(bincrates[2]-bincrates[1])/bincrates[1];
    jfreq = histogram(LR, HR,dim=['time'], bins=[LR_bins, HR_bins])
    jfq=jfreq/ndmat
    jpamtH=(jfreq*jfreq.HR_bin)/ndmat; jpamtL=(jfreq*jfreq.LR_bin)/ndmat
    weight1 = np.cos(np.deg2rad(jfreq.lat))
    del jfreq
    weight1 = weight1/weight1.sum()
    weight1.name = "weights"
    jhwt=jpamtH.weighted(weight1);jlwt=jpamtL.weighted(weight1);jfwt=jfq.weighted(weight1)
    del jpamtH
    del jpamtL
    jH=jhwt.mean(dim=["lon","lat"]);jL=jlwt.mean(dim=["lon","lat"]);jF=jfwt.mean(dim=["lon","lat"])
    out_jdist=xr.Dataset({"jdL": jL,"jdH": jH, "jdF": jF})
    return out_jdist

for lr in lr_list:
    high_res = 10  ## spatial resolution of high resolution dataset in kilometers
    low_res = lr #100 ## spatial resolution of low res dataset in kilometers
    HR= xr.open_mfdataset('/level01_indata/imerg_'+str(high_res)+'km/*.nc', parallel=False) 
    LR = xr.open_mfdataset('/level01_indata/imerg_nearest/nearest_'+str(high_res)+'km/imerg_'+str(low_res)+'km/*.nc', parallel=False)
    HR = HR.chunk({"lat": 50, "lon": 50, "time": -1})  # moderate chunk size
    LR = LR.chunk({"lat": 50, "lon": 50, "time": -1})
    HR=HR.rename({"precipitation": "HR"})
    LR=LR.rename({"precipitation": "LR"})

    HR1=HR.HR
    LR1=LR.LR
    del HR
    del LR
    ## Rearranging the dimensions to a common format
    HR2=HR1.transpose('lon','lat','time')
    LR2=LR1.transpose('lon','lat','time')
    HR2 = HR2.persist()
    LR2 = LR2.persist()
    del LR1
    del HR1

    out_jdist=makejointdist(HR2,LR2)
    out_jdist = out_jdist.persist()
    jdist_data=client.gather(client.compute(out_jdist))

    jdL = jdist_data.jdL
    jdH = jdist_data.jdH
    jdF = jdist_data.jdF
    bincrates = jdist_data.HR_bin

xr.Dataset({"jdL": jdL,"jdH": jdH, "jdF": jdF}).to_netcdf(path='/data/rainjointdist_data_'+str(high_res)+'_'+str(low_res)+'km.nc')
print ('finished saving nc file')
