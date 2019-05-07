#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 13:56:52 2019

@author: cbegeman
"""

import sys
import os
import netCDF4
import datetime
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from matplotlib import cm
from math import pi

def transect(latS,lonW,var,yr,mo,varlim=False):# user-defined parameters
#lat_transect = [-78, -78]
#lonW = [30,30]

    placename = ( str(latS[0]) + 'S' + str(lonW[0]) + 'W-' + 
                  str(latS[1]) + 'S' + str(lonW[1]) + 'W' )
    timename = str(yr) + '-' + str(mo)
    
    lat_transect = np.multiply(-1.,latS)
    #lon_transect = [360-60, 360-60]
    lon_transect = np.subtract(360,lonW)
    
    lat_N = -74 # northern limit of domain
    
    fmesh = netCDF4.Dataset('../oEC60to30v3wLI60lev.171031.nc')
    #fmesh=netCDF4.Dataset('/project/projectdirs/acme/inputdata/ocn/mpas-o/oEC60to30v3wLI/oEC60to30v3wLI60lev.171031.nc')
    f = netCDF4.Dataset('/usr/projects/climate/mhoffman/e3sm/cryo-campaign-data/mpaso.hist.am.timeSeriesStatsMonthly.0070-01-01.nc')
    
    # constants
    deg2rad  = pi/180.
    vartitle = ['T','S','rho','u','v']
    varname  = ['timeMonthly_avg_activeTracers_temperature',
                'timeMonthly_avg_activeTracers_salinity',
                'timeMonthly_avg_potentialDensity',
                'timeMonthly_avg_velocityZonal',
                'timeMonthly_avg_velocityMeridional']
    varmin = [-2.5,30,1020,-0.01,-0.01]
    varmax = [1.5,35,1030,0.01,0.01]
    dlat = 0.15 # at 30km resolution, distance between cells in latitude space
    dlon = 0.9
    bad_data = -1e33
    bad_data2 = 0.
    
    # import variables from file
    latCell  = fmesh.variables['latCell'][:]
    lonCell  = fmesh.variables['lonCell'][:]
    idxCell  = fmesh.variables['indexToCellID'][:]
    xCell    = fmesh.variables['xCell'][:]
    yCell    = fmesh.variables['yCell'][:]
    depths   = fmesh.variables['refBottomDepth'][:]
    kmax     = fmesh.variables['maxLevelCell'][:]
    zmax     = np.multiply(-1,fmesh.variables['bottomDepth'][:])
    zh       = fmesh.variables['layerThickness'][0,:]
    icemask  = fmesh.variables['landIceMask'][:]
    zice     = fmesh.variables['landIceDraft'][0,:]
    data     = f.variables[varname[vartitle.index(var)]][0,:]
    ssh      = f.variables['timeMonthly_avg_ssh'][0,:]
    
    # calculate z from depths
    z        = np.zeros(depths.shape)
    z[0]     = -0.5 * depths[0]
    z[1:]    = -0.5 * (depths[0:-1] + depths[1:])
    zbottom  = np.zeros(zh.shape)
    zbottom[:,-1] = zmax
    for i in range(len(depths)-2,-1,-1):
        zbottom[:,i] = zbottom[:,i+1] + zh[:,i+1]
    zmid = zbottom + np.multiply(0.5,zh)
    zssh = zbottom[:,0] + zh[:,0]
    # define line of constant latitude
    if lat_transect[0] == lat_transect[1]:
        lat_transect[0] = lat_transect[0] - dlat
        lat_transect[1] = lat_transect[1] + dlat
    if lon_transect[0] == lon_transect[1]:
        lon_transect[0] = lon_transect[0] - dlon
        lon_transect[1] = lon_transect[1] + dlon
    
    # define plot location
    
    # northern limit for subplots
    logical_N = (latCell < lat_N*deg2rad) & (xCell > 0)
    
    # indices of transect
    logical_trans = ( (latCell > lat_transect[0]*deg2rad) & 
                      (latCell < lat_transect[1]*deg2rad) &
                      (lonCell > lon_transect[0]*deg2rad) & 
                      (lonCell < lon_transect[1]*deg2rad)   )
    idx_trans = np.where(logical_trans)[0]
    
    idx1 = np.argmin(yCell[logical_trans])
    temp = np.sqrt( np.square(yCell[logical_trans] - yCell[logical_trans][idx1]) + 
                    np.square(xCell[logical_trans] - xCell[logical_trans][idx1])   )
    idxsort_trans = idx_trans[temp.argsort()]
    ysort_trans = yCell[idxsort_trans]
    xsort_trans = xCell[idxsort_trans]
    dist_trans = temp[temp.argsort()]
    
    # distance along transect
    
    # create mesh variables for plotting
    ymesh,temp = np.meshgrid(dist_trans, depths);
    zmesh = np.transpose(zmid[idxsort_trans])
    data_trans = np.transpose(data[idxsort_trans,:])
    data_trans_masked = np.transpose(data[idxsort_trans,:])
    data_trans_zmasked = np.transpose(data[idxsort_trans,:])
    # Ideally, mask both bad data and ice shelf
    #data_trans_masked = np.ma.masked_where( (data_trans < bad_data) |
    #                                        (zmesh > zicemesh), data_trans)
    data_trans_masked = np.ma.masked_where( (data_trans < bad_data) |
            (data_trans == bad_data2), data_trans)
    for idx,i in enumerate(idxsort_trans):
        data_trans_zmasked[:,idx] = np.ma.masked_where( 
                (zmid[i,:] < zmid[i,kmax[i]-1]), data[i,:])
    mask = np.ma.getmask(data_trans_masked)
    
    temp1 = kmax[logical_trans]
    temp2 = kmax[idxsort_trans]
    # plots
    
    # show profile line across cells
    fig1 = plt.figure()
    plt.plot(yCell[logical_N],     xCell[logical_N], 'k.')
    plt.plot(yCell[logical_trans], xCell[logical_trans], 'r.')
    plt.axis('equal')
    plt.savefig('grid_' + placename + '_' + timename + '.png')
    plt.close()
    
    fig = plt.figure()
    cntr1 = plt.tricontourf(yCell[logical_N].flatten(), xCell[logical_N].flatten(), 
                            zmax[logical_N].flatten(), levels=20, cmap="viridis")
#    cntri = plt.tricontourf(yCell[logical_N].flatten(), xCell[logical_N].flatten(), 
#                           zice[logical_N].flatten(), levels = 10, cmap="viridis")
    plt.plot(yCell[logical_N],     xCell[logical_N], 'o', color = 'white', 
             markersize = 4, fillstyle = 'none')#, alpha = 0.5)
    cntr = plt.tricontour(yCell[logical_N].flatten(), xCell[logical_N].flatten(), 
                           zice[logical_N].flatten(), [-1e-10], colors = 'k')
    plt.plot(yCell[idxsort_trans], xCell[idxsort_trans], 'k-')
    plt.axis('equal')
    cbar = plt.colorbar(cntr1)
    cbar.set_label('Depth (m)')    
    plt.savefig('bathy_' + placename + '_' + timename + '.png')
    plt.close()
#    plt.scatter(np.divide(ymesh,1e3), zmesh, s=5, 
#                c=data_trans_masked, cmap = 'viridis') #vmin=varmin[vartitle.index(var)], vmax=varmax[vartitle.index(var)], 
#    plt.plot(np.divide(dist_trans,1e3), ssh[idxsort_trans], color = 'blue', marker = '.', linestyle = '-')
#    plt.plot(np.divide(dist_trans,1e3), zmax[idxsort_trans], color = 'black', marker = '.', linestyle = '-')
#    #plt.plot(np.divide(dist_trans,1e3), zmid[idxsort_trans,kmax[idxsort_trans]-1], color = 'blue', marker = '.', linestyle = '-')
#    cbar = plt.colorbar()
#    cbar.set_label(var)
#    plt.xlabel('Distance (km)')
#    plt.ylabel('Depth (m)')
    
    yline = np.divide(dist_trans,1e3)
    yfill = np.append(yline[0],yline)
    yfill = np.append(yfill,yline[-1])
    sshfill = np.append(0,ssh[idxsort_trans])
    sshfill = np.append(sshfill,0)
    bathymax = np.min(zmax[idxsort_trans]) - 100
    bathyfill = np.append(bathymax,zmax[idxsort_trans])
    bathyfill = np.append(bathyfill,bathymax)
    
    fig2 = plt.figure()
    cntr2 = plt.tricontourf(np.divide(ymesh[~mask].flatten(),1e3), zmesh[~mask].flatten(), 
                            data_trans_zmasked[~mask].flatten(), levels=14, cmap="viridis")
    plt.plot(yline, ssh[idxsort_trans], color = 'blue', marker = '.', linestyle = '-')
    plt.fill(yfill, sshfill, c = 'white', alpha = 0.8)
    plt.plot(np.divide(dist_trans,1e3), zmax[idxsort_trans], color = 'black', marker = '.', linestyle = '-')
    plt.fill(yfill, bathyfill, c = 'black', alpha = 0.8)
    if varlim:
        plt.clim([varmin[vartitle.index(var)], varmax[vartitle.index(var)]])
    cbar = plt.colorbar()
    cbar.set_label(var)
    plt.xlabel('Distance (km)')
    plt.ylabel('Depth (m)')
    plt.savefig(var + '_' + placename + '_' + timename + 'lim' + str(varlim) + 
                '.png')
    plt.close()
    #plt.savefig('test_transect.png')
    
    #fig = plt.figure()
    #plt.scatter(yCell[logical_N], xCell[logical_N], s=5, c = zice[logical_N], cmap = 'viridis') # c=lonCell[idx1]/deg2rad
    #plt.colorbar()
    #plt.axis('equal')
    #plt.title('Land Ice Draft (m)')
    #
    #fig = plt.figure()
    #plt.scatter(yCell[logical_N], xCell[logical_N], s=5, c = ssh[logical_N], cmap = 'viridis') # c=lonCell[idx1]/deg2rad
    #plt.colorbar()
    #plt.axis('equal')
    #plt.title('Average SSH (m)')
    #
    #fig = plt.figure()
    #plt.scatter(yCell[logical_N], xCell[logical_N], s=5, c = zmax[logical_N], cmap = 'viridis') # c=lonCell[idx1]/deg2rad
    #plt.colorbar()
    #plt.axis('equal')
    #plt.title('Bottom depth (m)')
    #
    #fig = plt.figure()
    #plt.scatter(yCell[logical_N], xCell[logical_N], s=5, c = zssh[logical_N], cmap = 'viridis') # c=lonCell[idx1]/deg2rad
    #plt.colorbar()
    #plt.axis('equal')
    #plt.title('Water column thickness (m)')