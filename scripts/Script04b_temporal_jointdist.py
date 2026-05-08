### This is the script for estimating the joint distribution of rain amounts at high and low resolutions.
### This script should be executed following Script03. It can also be executed following Script02 since all required inputs 
### should already be available. The basic logic behind the script is to loop through the rain rates at HR and LR
### and for each grid which satisify those rain rate conditions, find the rain amount in 1) LR dataset and 2) HR dataset.
### The input for this script is the HR dataset and the downscaled (Script02) LR dataset.
### The output should be a plot showing the joint distribution of rain amounts at HR and LR.

import xarray as xr
import numpy as np
from xhistogram.xarray import histogram


res = ['1min', '2min', '5min', '10min', '30min', '1hr', '3hr', '6hr', '12hr', 'day']

def makejointdist(HR,LR):
    ndmat=len(HR.time)
    L=2.5e6
    maxp=1500;# % choose an arbitrary upper bound for initial distribution, in w/m2
    minp=.001;# .                                                     
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
    bins=bincrates[:-1]
    LR_bins=bins
    HR_bins=bins
    db=(bincrates[2]-bincrates[1])/bincrates[1];
    jfreq = histogram(LR, HR,dim=['time'], bins=[LR_bins, HR_bins])
    jfq=jfreq/ndmat
    jpamtH=(jfreq*jfreq.HR_bin)/ndmat; jpamtL=(jfreq*jfreq.LR_bin)/ndmat
    jL = jpamtL; jH = jpamtH; jF = jfq;
    out_jdist=xr.Dataset({"jdL": jL,"jdH": jH, "jdF": jF})
    return out_jdist



for hr in res:
    for lr in res[1:]:
        if hr == lr:
            continue
        HR= xr.open_dataset('./../data/temporal/cleaned_input/timeseries/manus_'+hr+'.nc') 
        LR = xr.open_dataset('./../data/temporal/cleaned_input/interped/manus_'+hr+'_nearest_' + lr + '.nc')
        HR=HR.rename({"precipitation": "HR"})
        LR=LR.rename({"precipitation": "LR"})
        HR1=HR.HR
        LR1=LR.LR
        jdist_data= makejointdist(HR1, LR1)
        jdL = jdist_data.jdL
        jdH = jdist_data.jdH
        jdF = jdist_data.jdF
        bincrates = jdist_data.HR_bin
        xr.Dataset({"jdL": jdL,"jdH": jdH, "jdF": jdF}).to_netcdf(path='./../data/temporal/output/jointdist/manus_jointdist_'+hr+'_' + lr + '.nc')
        print ('finished saving nc file for hr= '+hr+' and lr= '+lr)


