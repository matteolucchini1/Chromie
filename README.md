# CHROMIE

Chromie is a Python3 analysis pipeline for the Neutron Star Interior Composition Explorer (NICER) X-ray observatory, operating from the ISS.
It is designed to analyze a large number of observations, produce common spectral and timing products, and visualize these products
automatically. Chromie is essentially a successor of the Chromos pipeline for the RXTE observatory (https://github.com/davidgardenier/chromos).
The pipeline is tailored towards X-ray binary systems; in principle it can be used for any NICER observation but some products may
not be relevant to other objects.

---------------------------------------------------------------------------------------------------------------------------------------

## System requirements

Running Chromie requires installing common X-ray astronomy packages: HEASoft (version 6.32.1 or higher), including HEASoftPy
and PyXspec, Stingray (version 1.1.2 or higher), Astropy (version 4.2 or higher), Numpy and Matplotlib. After installing HEASOFT
make sure to set up your environment to analyze NICER data (https://heasarc.gsfc.nasa.gov/docs/nicer/analysis_threads/nicer-setup/).
Beyond the basic Python3 packages, you will need to download the data you want to analyze and place it in a single folder. This can
be done through the NICER master catalogue in the HEASARC archive (https://heasarc.gsfc.nasa.gov/W3Browse/nicer/nicermastr.html). Note
that if you have a HEASOFT version older than 6.32.1 installed, you may encounter issues when running nicerl2 for select observations.

---------------------------------------------------------------------------------------------------------------------------------------

## Running Chromie

Before running the pipeline, specify the path to your data folder in paths.py. The variable niderdatadir should be the folder where
you downloaded all the observations; you can use the variable source\_name to organize your data more easily. The variable obsid\_list 
should point to a file in the Obsid\_list folder with a list of NICER obsids (two files are provided as an exmple); this should be
identical to the observations you downloaded. By default, the pipeline will produce two folder (Logs and Products) in the nicerdatadir
path with all the products of the code. You will also need to set the correct path to the geomagnetic data folder in paths.py,
and update the path to your chromie installation in rebin\_spectra to point to the nicer\_channels\_to\_group.txt file.


After setting up the paths, Chromie runs through different modules to reduce the data from level-1 NICER files to publication-level
products. Each module can be run independently, provided the previous steps completed succesfully. The only exception is run\_nicerl2()
and extract\_spectra(); currently you always need to run the former before the latter due to weird behavior on HEASOFT, and you also 
always need to run set\_mkf() first. This will be fixed in a future version. 


Set\_mkf() moves the filter files and sets up the path to these files correctly. Run\_nicerl2 produces cleaned level-2 Event files, 
from which extract_spectra extracts the time averaged spectrum. These are then rebinned (rebin\_spectra) and fitted with a simple
spectrla model (spectral\_analysis). Extract\_timing runs simple timing analysis using the Stingray library, directly from the level-2
Event files. Finally, observation\_times and visualize\_data are used to plot how multiple quantities are varying from one observation
to the next. 

---------------------------------------------------------------------------------------------------------------------------------------
## Citing Chromie

PLACEHOLDER WIP

---------------------------------------------------------------------------------------------------------------------------------------
