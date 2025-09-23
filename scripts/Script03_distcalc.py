## Script for calculating distribution of rain amount and frequency (to be executed after Script02.py)
## Here the inputs are the high and low resolution versions of the dataset.
## The script employes dask array to process the large dataset and with a 100GB memory takes approximately 2 hours to compute the rain distribution for the entire globe.
## This is an upgrade from the previous versions where the script looped through lat-lon values to calculate the global average rainfall distributions.
## The output should be a rainfall amount and frequency distribution plot corresponding datasets of two resolutions
## This script primarily utilizes xarray. The part of the script utilizing numpy for weighting of the histograms has been commented out. 
## This script is also just a modification of the rain-metric-python script from Pendergrass & Deser 2017
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from xhistogram.xarray import histogram
from datetime import datetime



high_res = 10  ## spatial resolution of high resolution dataset in kilometers
low_res = 100 #100 ## spatial resolution of low res dataset in kilometers

startTime = datetime.now()
## Reading in the data (high & low res)
HR= xr.open_mfdataset('/level01_indata/imerg_'+str(high_res)+'km/*.nc',parallel=False) 
LR = xr.open_mfdataset('/level01_indata/imerg_'+str(low_res)+'km/*.nc',parallel=False)
HR1=HR.precipitation
LR1=LR.precipitation
## Rearranging the dimensions to a common format
HR2=HR1.transpose('lon','lat','time')
LR2=LR1.transpose('lon','lat','time')
del LR1; del HR1
LR2.load() ## dechunking at the beginning to speed up the script. This might need to be commented out 
HR2.load() ## and dechunking should be done at the end when the dataset size increases (needs checking)
L=2.5e6

def makedists(pdata,binl):
    ##### This is called from within makeraindist. The function is an updated version of the same from Pendergrass & Hartmann, 2014
    ##### Calculate distributions 
    bins=binl
    # this is the histogram - we'll get frequency from this
    thisn=histogram(pdata,dim=['time'], bins=[bins],block_size=None) 
    #### Calculate the number of days with non-missing data, for normalization
    ndmat=thisn.sum(dim='precipitation_bin')
    thisppdfmap=thisn/ndmat
    #### Iterate back over the bins and add up all the precip - this will be the rain amount distribution
    testpamtmap=(thisn*thisn.precipitation_bin) ## This method is faster to process for the actual calculation (but will require more memory if not performed using dask array)
    thispamtmap=testpamtmap/ndmat
    return thisppdfmap,thispamtmap


def makeraindist(pdata1,pdata2):
    ### The function is from Pendergrass & Hartmann, 2014
    #### 1. Calculate bin structure. Note, these were chosen based on daily CMIP5 data - if you're doing something else you might want to change it
    pmax=np.array([pdata1.max(),pdata2.max()]).max()
    #print('pmax calculated')
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
    #### 2. Calculate distributions 
    ppdfmap,pamtmap=makedists(pdata1,bincrates);
    ppdfmap2,pamtmap2=makedists(pdata2,bincrates);

    
    weight1 = np.cos(np.deg2rad(ppdfmap.lat));weight2 = np.cos(np.deg2rad(ppdfmap2.lat))
    weight1 = weight1/weight1.sum();weight2 = weight2/weight2.sum()
    weight1.name = "weights";weight2.name = "weights"
    weightp1 = ppdfmap.weighted(weight1); weightp2 = ppdfmap2.weighted(weight2)
    ppdf1 = weightp1.mean(("lon", "lat")); ppdf2 = weightp2.mean(("lon", "lat"))
    weightpa1 = pamtmap.weighted(weight1);weightpa2 = pamtmap2.weighted(weight2)
    pamt1 = weightpa1.mean(("lon", "lat"));pamt2 = weightpa2.mean(("lon", "lat"))
    
    return ppdf1,pamt1,ppdf2,pamt2,bincrates


### Execute only the first line if running for entire globe
ppdfL, pamtL, ppdfH, pamtH, bincrates = makeraindist(LR2,HR2)
del LR2; del HR2
print ('saving nc file')

xr.Dataset({"pamtH": pamtH,"pamtL": pamtL,"ppdfH": ppdfH,"ppdfL": ppdfL}).to_netcdf(path='/data/raindist_data_'+str(high_res)+'_'+str(low_res)+'km.nc')
print ('finished saving nc file')


print(datetime.now() - startTime)

