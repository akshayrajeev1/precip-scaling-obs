## Script for calculating rain amount distributions at each grid and zonal distributions
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from xhistogram.xarray import histogram
from dask.distributed import LocalCluster, Client
import dask


dask.config.set(temporary_directory='/tmp')
cluster = LocalCluster(n_workers=3, threads_per_worker=1, memory_limit='50GB')
client = Client(cluster)
print("Dashboard:", client.dashboard_link, flush=True)
def makemap(pdata,binl):
        ##### This is called from within makeraindist.
        ##### Calculate distributions 
        bins=binl#np.append(0,binl)
        # this is the histogram - we'll get frequency from this
        thisn=histogram(pdata,dim=['time'], bins=[bins],block_size=None) 
        #### Calculate the number of days with non-missing data, for normalization
        ndmat=thisn.sum(dim='precipitation_bin')
        thisppdfmap=thisn/ndmat
        #### Iterate back over the bins and add up all the precip - this will be the rain amount distribution
        testpamtmap=(thisn*thisn.precipitation_bin) ## This method is faster to process for the actual calculation (but will take way longer and more memory) try: #pdata.groupby_bins(pdata,bins).sum(dim='time')  
        thispamtmap=testpamtmap/ndmat
        return thisppdfmap,thispamtmap
def makezonal(pdata,binl):
    ##### This is called from within makeraindist.
    ##### Calculate distributions 
    weight1 = np.cos(np.deg2rad(pdata.lat))
    weight1 = weight1/weight1.sum()
    weight1.name = "weights"
    bins=binl#np.append(0,binl)
    # this is the histogram - we'll get frequency from this
    thisn=histogram(pdata,dim=['time','lon'], bins=[bins],block_size=None,weights=weight1) 
    #### Calculate the number of days with non-missing data, for normalization
    ndmat=thisn.sum(dim='precipitation_bin')
    thisppdfmap=thisn/ndmat
    #### Iterate back over the bins and add up all the precip - this will be the rain amount distribution
    testpamtmap=(thisn*thisn.precipitation_bin) ## This method is faster to process for the actual calculation (but will take way longer and more memory) try: #pdata.groupby_bins(pdata,bins).sum(dim='time')  
    thispamtmap=testpamtmap/ndmat
    return thisppdfmap,thispamtmap
def distmap(pdata1): 
    L=2.5e6
    #### 1. Calculate bin structure. Note, these were chosen based on daily CMIP5 data - if you're doing something else you might want to change it
    #print('starting...')
    #pmax=np.array([pdata1.max(),pdata2.max()]).max()
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
    #print("bincrates done")
    #### 2. Calculate distributions 
    #print("Calculating Distributions")
    ppdfmap,pamtmap=makemap(pdata1,bincrates);
    del pdata1

    outmap=xr.Dataset({"pamt": pamtmap,"ppdf": ppdfmap})
    
    return outmap
def zonaldist(pdata1): 
    L=2.5e6
    #### 1. Calculate bin structure. Note, these were chosen based on daily CMIP5 data - if you're doing something else you might want to change it
    #print('starting...')
    #pmax=np.array([pdata1.max(),pdata2.max()]).max()
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
    #print("bincrates done")
    #### 2. Calculate distributions 
    #print("Calculating Distributions")
    ppdfz,pamtz=makezonal(pdata1,bincrates);
    del pdata1

    zonaldist=xr.Dataset({"pamt": pamtz,"ppdf": ppdfz})
    
    return zonaldist

for res in [10,100]:
    print("Resolution:", res)
    if res==10:
        data1 = xr.open_mfdataset('/level01_indata/IMERG_V07B/imerg_'+str(res)+'km/*.nc',parallel=False)
    else:
        data1 = xr.open_mfdataset('/level01_indata/imerg_nearest/nearest_10km/imerg_'+str(res)+'km/*.nc',parallel=False)
    
    data1 = data1.chunk({"time": 365,"lat": 50,"lon":50})
    datamap1=data1.precipitation
    del data1
    ## Rearranging the dimensions to a common format
    datamap1=datamap1.transpose('lon','lat','time')

    out_map = distmap(datamap1)
    out_zonal = zonaldist(datamap1)
    map_data=client.gather(client.compute(out_map))
    zonal_data=client.gather(client.compute(out_zonal))

    map_data.to_netcdf(path='/level02_indata/distmap_'+str(res)+'km_10v.nc') ## Here level-02 is an intermediate level between the gridded dataset and the final data that is plotted
    zonal_data.to_netcdf(path='/level02_indata/distzonal_'+str(res)+'km_10v.nc')

