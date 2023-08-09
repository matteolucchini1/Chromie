from Functions.set_mkf import *
from Functions.run_nicerl2 import *
from Functions.extract_spectra import *
from Functions.extract_timing import *
from Functions.observation_times import *
from Functions.rebin_spectra import *
from Functions.spectral_analysis import *
from Functions.visualize_data import*

mkf=set_mkf()
run_nicerl2(mkf)
extract_spectra(mkf)
rebin_spectra()
spectral_analysis()
extract_timing()
observation_times()
visualize_data()
