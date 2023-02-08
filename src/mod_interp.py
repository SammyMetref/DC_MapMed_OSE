import xarray as xr
import numpy as np
import pyinterp
import netCDF4

#import sys
#sys.path.append('.')
from src.mod_inout import *


def interp_on_alongtrack(gridded_dataset, 
                         ds_alongtrack,
                         lon_min=0., 
                         lon_max=360., 
                         lat_min=-90, 
                         lat_max=90., 
                         time_min='1900-10-01', 
                         time_max='2100-01-01',
                         is_circle=True, 
                         is_ssh=True):
    
    # Interpolate maps onto alongtrack dataset
    if isinstance(gridded_dataset, str):
        
        issla = not is_ssh
            
        x_axis, y_axis, z_axis, grid = read_l4_dataset(gridded_dataset,
                                                       lon_min=lon_min,
                                                       lon_max=lon_max, 
                                                       lat_min=lat_min,
                                                       lat_max=lat_max, 
                                                       time_min=time_min,
                                                       time_max=time_max,
                                                       is_circle=is_circle,
                                                       issla=issla)
         
    elif isinstance(gridded_dataset, list):
        
        x_axis, y_axis, z_axis, grid = read_l4_dataset_from_aviso(gridded_dataset[0],
                                                                  gridded_dataset[1],
                                                                  lon_min=lon_min,
                                                                  lon_max=lon_max, 
                                                                  lat_min=lat_min,
                                                                  lat_max=lat_max, 
                                                                  time_min=time_min,
                                                                  time_max=time_max,
                                                                  is_circle=is_circle)
         
    
    ssh_map_interp = pyinterp.trivariate(grid, 
                                         ds_alongtrack["longitude"].values, 
                                         ds_alongtrack["latitude"].values,
                                         z_axis.safe_cast(ds_alongtrack.time.values),
                                         bounds_error=False).reshape(ds_alongtrack["longitude"].values.shape) 
     
    
    ssh_alongtrack = (ds_alongtrack["sla_unfiltered"]+ds_alongtrack["mdt"]).values 
    lon_alongtrack = ds_alongtrack["longitude"].values
    lat_alongtrack = ds_alongtrack["latitude"].values
    time_alongtrack = ds_alongtrack["time"].values
    
    # get and apply mask from map_interp & alongtrack on each dataset
    msk1 = np.ma.masked_invalid(ssh_alongtrack).mask
    msk2 = np.ma.masked_invalid(ssh_map_interp).mask
    msk = msk1 + msk2
    
    ssh_alongtrack = np.ma.masked_where(msk, ssh_alongtrack).compressed()
    lon_alongtrack = np.ma.masked_where(msk, lon_alongtrack).compressed()
    lat_alongtrack = np.ma.masked_where(msk, lat_alongtrack).compressed()
    time_alongtrack = np.ma.masked_where(msk, time_alongtrack).compressed()
    ssh_map_interp = np.ma.masked_where(msk, ssh_map_interp).compressed()
    
    # select inside value (this is done to insure similar number of point in statistical comparison between methods)
    indices = np.where((lon_alongtrack >= lon_min+0.01) & (lon_alongtrack <= lon_max-0.01) &
                       (lat_alongtrack >= lat_min+0.01) & (lat_alongtrack <= lat_max-0.01))[0]
    
    return time_alongtrack[indices], lat_alongtrack[indices], lon_alongtrack[indices], ssh_alongtrack[indices], ssh_map_interp[indices]
    