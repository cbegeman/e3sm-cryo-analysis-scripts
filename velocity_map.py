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
#cmaps = cmocean.cm.cmap_d

# PARAMETERS

#zi = 0.;
zi = 400.;
zeval = np.arange(0,1200,100);
#var = ['T']
var = ['U']
#var = ['tau']
#var = ['ssh']
#var = ['rho']
run = ['ISMF','ISMF-noEAIS']
#run = ['ISMF-noEAIS']
yr = [73]
pt = 'quiver'
#pt = 'abs'
#yr = np.arange(70,90,1)
#yr = np.arange(70,101,1)
#mo = np.arange(1,13,1)
mo = [8]
#loc = 'fris'
loc = 'frisEAcoast'

for k in yr:
    for m in mo:
        for j in var:
            for zi in zeval:
                wed.plot_surf_var(j,k,m,z=zi,run=run[0],zab=False,runcmp=True,locname=loc,varlim=True,plottype=pt)
                for i in run:
                    wed.plot_surf_var(j,k,m,z=zi,run=i,zab=False,runcmp=False,locname=loc,varlim=True,plottype=pt)

