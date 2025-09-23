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

def calcbo(LRdist,HRdist,bincrates):
    scH=np.cumsum(HRdist)/np.sum(HRdist)
    scL=np.cumsum(LRdist)/np.sum(LRdist)
    rH = np.interp(0.5, scH, bincrates)
    rL = np.interp(0.5, scL, bincrates)
    bo = 100*((rH-rL)/rL)
    # centroids for further calculation
    lnrh2 = np.interp(.5, scH, np.log(bincrates))
    lnrh1 = np.interp(.5, scL, np.log(bincrates))
    db=(bincrates[2]-bincrates[1])/bincrates[1]  
    # calculate dp/dln(r)
    nb=len(LRdist);
    dpdlnrc= np.concatenate((np.array([0]),LRdist[2:nb]-LRdist[0:(nb-2)],np.array([0])))/(2*db) # centered difference (2nd order accurate; now used near endpoints)
    prm2=LRdist[:(nb-4)]
    prm1=LRdist[1:(nb-3)]
    prp1=LRdist[3:(nb-1)]
    prp2=LRdist[4:]
    dpdlnr= np.concatenate((np.array([0]),np.array([0]),8*(prp1-prm1)-(prp2-prm2),np.array([0]),np.array([0])))/(12*db) # 4th order accurate 
    dpdlnr[1]=dpdlnrc[1] # fill in with second order accurate near endpoints
    dpdlnr[nb-2]=dpdlnrc[nb-2] 
    dpamt=HRdist-LRdist

    xp = np.log(bincrates[1:]) - lnrh1
    b = lnrh2 - lnrh1
    pamtbo = np.zeros(LRdist.shape)
    pamtbo[1:] = np.interp(xp - b, xp, LRdist[1:])
    #pamtbo[1:]=-(bo/100)*dpdlnr[1:]+LRdist[1:]
    err=100*np.nansum(np.abs(pamtbo[2:]-HRdist[2:]))/np.nansum(np.abs(dpamt[2:]))
    return (bo, err)
high_res = 10
low_res = 100
distm10 = xr.open_mfdataset('/level02_indata/distmap_'+str(high_res)+'km_10v.nc')
distm100 = xr.open_mfdataset('/level02_indata/distmap_'+str(low_res)+'km_10v.nc')
pamtmapH=distm10.pamt[:,:,1:]
pamtmapL=distm100.pamt[:,:,1:]
bincrates=distm10.precipitation_bin[1:]
pamtmapH = pamtmapH.chunk({'lon': 50, 'lat': 50})
pamtmapL = pamtmapL.chunk({'lon': 50, 'lat': 50})

bo_val,err_val = xr.apply_ufunc(
calcbo,
pamtmapL,
pamtmapH,
bincrates,
input_core_dims=[['precipitation_bin'],['precipitation_bin'],['precipitation_bin']],
output_core_dims=[[], []],  # scalar output
vectorize=True,
dask='parallelized',  # optional for large data
output_dtypes=[float, float])
bom, errm = client.gather(client.compute([bo_val,err_val]))
xr.Dataset({"shift": bom,"error": errm}).to_netcdf(path='/data/bo_'+str(high_res)+'_'+str(low_res)+'km_10v.nc')
