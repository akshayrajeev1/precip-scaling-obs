### Temporal Interpolation Script
### This script is to perform temporal interpolation of the timeseries data (to be executed following Script01)
### The basic logic behind the script is to read in the data at very high resolution and then resample it to various temporal resolutions (2min, 5min, 10min, 30min, 1hr, 3hr, 6hr, 12hr, 1day) using mean resampling method.
import xarray as xr
import numpy as np

res = ['1min', '2min', '5min', '10min', '30min', '1hr', '3hr', '6hr', '12hr', 'day']

for hr in res:
    for lr in res[1:]:
        if hr == lr:
            continue
        HR = xr.open_dataset('./../data/temporal/cleaned_input/timeseries/manus_' + hr + '.nc')
        LR = xr.open_dataset('./../data/temporal/cleaned_input/timeseries/manus_' + lr + '.nc')

        interp = LR.interp(time=HR.time,method='nearest',kwargs={"fill_value": "extrapolate"})
        interp.to_netcdf(path='./../data/temporal/cleaned_input/interped/manus_'+hr+'_nearest_' + lr + '.nc')