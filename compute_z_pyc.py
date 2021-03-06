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
import matplotlib
import matplotlib.pyplot as plt
import scipy.signal
import cmocean
from matplotlib import cm
from math import pi
from matplotlib.colors import LogNorm

import weddell_mod as wed
from pick_from_mesh import pick_from_region
from plot_config import *
#cmaps = cmocean.cm.cmap_d

# PARAMETERS

var = ['z_pyc']
run = ['ISMF','ISMF-noEAIS']
yr = [70,101]
loc = 'wed_pyc_Ryan'
#zlim_shelf = [-500,10]#n=57
#zlim_shelf = [-2000,-1000]#n=21
zlim_shelf = [-2000,-500]#n=50
#zlim_deep = [-3500,-1000]#n=84
#zlim_deep = [-4500,-2500]# n=136
zlim_deep = [-4500,-3500]# n=94

filenames= [
            'ISMF_zpyc_wed_pyc_Ryan_70-101_zlim-2000--500',
#            'ISMF_zpyc_wed_pyc_Ryan_70-101_zlim-2000--1000',
#            'ISMF_zpyc_wed_pyc_Ryan_70-101_zlim-500-10',
#            'ISMF_zpyc_wed_pyc_Ryan_70-101_zlim-4500--2500']
#            'ISMF_zpyc_wed_pyc_Ryan_70-101_zlim-4500--2500']
            'ISMF_zpyc_wed_pyc_Ryan_70-101_zlim-3500--1000']
filename_T = 'ISMF_TS_20mab_76S30W_70-101'

#get_number_samples = True
get_number_samples = False
#-----------------------------------------------------------
if get_number_samples:
    mask_ice = False
    #zlim = zlim_deep
    zlim = zlim_shelf
    
    fmesh = netCDF4.Dataset(meshpath[runname.index(run[0])])
    
    idx = pick_from_region(region=loc,run=run[0])
    #print('Number of points in pyc domain = ',len(idx))
    
    zmax     = np.multiply(-1,fmesh.variables['bottomDepth'][idx])
    idx = idx[zmax >= zlim[0]]
    zmax     = np.multiply(-1,fmesh.variables['bottomDepth'][idx])
    idx = idx[zmax < zlim[1]] 
    #print('Number of points in domain after depth filtering = ',len(idx))
    
    if mask_ice:
        landicemask  = fmesh.variables['landIceMask'][0,idx]
        #idx = idx[zice==0] 
        idx = idx[landicemask==0] 
    print('Number of points in domain after filtering = ',len(idx))
#-----------------------------------------------------------

#wed.pycnocline_depth_t(yr,run_list=run,region=loc,plot_histogram=False,zlim=zlim_shelf)
#wed.pycnocline_depth_t(yr,run_list=run,region=loc,plot_histogram=False,zlim=zlim_deep)

wed.plot_zpyc_t(filenames,run=run,tlim=[70,100],placename=['on-shelf','off-shelf'])
wed.plot_zpyc_t(filenames,run=run,tlim=[70,100],placename=['on-shelf','off-shelf'],plot_difference = True)
#wed.plot_zpyc_corr(filenames[0],filename_T,run=run)
#wed.plot_zpyc_corr(filenames[1],filename_T,run=run)

