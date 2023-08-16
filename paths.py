import os
import numpy as np

source_name = "J1820_all"
obsid_list = np.genfromtxt("Obsid_list/"+source_name+".lst",dtype='U21')
#note: this is used to treat cases when the user picks an individual obsid
obsid_list = np.array(obsid_list, ndmin=1, copy=False)
nicerdatadir = '/home/matteo/Data/'+source_name+'/'

#specify Geomagnetic path for spectral extraction
geomag_path = "/home/matteo/Software/Geomag/"

#place final products in a new subdirectories
productdir = nicerdatadir+'Products/'
if not os.path.exists(productdir):
    os.makedirs(productdir)
    print(f'Created {productdir}')

plotdir = productdir+'Plots/'
if not os.path.exists(plotdir):
    os.makedirs(plotdir)
    print(f'Created {plotdir}')

specplotir = plotdir+'Spectra/'
if not os.path.exists(specplotir):
    os.makedirs(specplotir)
    print(f'Created {specplotir}')
    
lcplotir = plotdir+'Lightcurves/'
if not os.path.exists(lcplotir):
    os.makedirs(lcplotir)
    print(f'Created {lcplotir}')

psdplotir = plotdir+'PSDs/'
if not os.path.exists(psdplotir):
    os.makedirs(psdplotir)
    print(f'Created {psdplotir}')

specdir = productdir+'Spectra/'
if not os.path.exists(specdir):
    os.makedirs(specdir)
    print(f'Created {specdir}')

psdir = productdir+'PSDs/'
if not os.path.exists(psdir):
    os.makedirs(psdir)
    print(f'Created {psdir}')

#create log directory and set up logs
logdir = nicerdatadir+'Logs/'
if not os.path.exists(logdir):
    os.makedirs(logdir)
    print(f'Created {logdir}')
terminal_output = True

obsdir=[]    
for i in range(obsid_list.size):
    nicerobsID = obsid_list[i]
    obsdir.append(nicerdatadir+nicerobsID)

#set l2 output directory - same as obsids by default
outdir =  obsdir
