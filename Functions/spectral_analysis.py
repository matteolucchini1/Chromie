from xspec import *

def spectral_analysis():

    import os
    import paths
    import logs
    logs.output("spectral_analysis")
    print("Running spectral analysis:")
    
    #Xspec settings:
    Xset.abund = "wilm"
    Xset.cosmo = "67.4 -0.5275 0.685"
    Xset.xsect = "vern"
    Xset.parallel.leven = 1
    Xset.chatter = 10
    #this needs to be set by hand because xspec is annoying
    Xset.openLog(paths.logdir+"spectral_analysis.log")
    Fit.method = "leven 1000"
    Fit.query = "no"
    
    #clean up count rate output files
    ratepath=paths.productdir+paths.source_name+"*countrates.dat"
    print(ratepath)
    string="rm -r "+ratepath
    os.system(string)
    
    for index in range(len(paths.obsid_list)):
        spectrum_file=paths.specdir+paths.obsid_list[index]+"_rebin.pha"
        rmf_file=paths.specdir+paths.obsid_list[index]+"_rmf.pha"
        arf_file=paths.specdir+paths.obsid_list[index]+"_arf.pha"
        bkg_file=paths.specdir+paths.obsid_list[index]+"_bkg.pha"        
        spectrum=Spectrum(spectrum_file,respFile=rmf_file,arfFile=arf_file)
        spectrum.background = bkg_file
        
        print("Calculating count rates: ")
        #get count rates in three energy bands and save them
        #0.3 to 3 keV:
        spectrum.ignore("**-0.3")
        spectrum.ignore("3.-**") 
        rate_low = spectrum.rate[0]
        rate_low_err = spectrum.rate[1]
        #3 to 10 keV: 
        spectrum.ignore("0.3-3.0")
        spectrum.notice("3.0-12.0")
        rate_high = spectrum.rate[0]
        rate_high_err = spectrum.rate[1]
        #RXTE-like band 1: 3 to 6 keV
        spectrum.ignore("3.0-12.0")
        spectrum.notice("3.0-6.0")
        RXTE_rate_low = spectrum.rate[0]
        RXTE_rate_low_err = spectrum.rate[1]
        #RXTE-like band 2: 6 to 10 keV
        spectrum.ignore("3.0-6.0")
        spectrum.notice("6.0-12.0")
        RXTE_rate_high= spectrum.rate[0]
        RXTE_rate_high_err = spectrum.rate[1]  
        #full band: 0.3 to 10 keV
        spectrum.notice("0.3-10.0")
        rate_full = spectrum.rate[0]
        rate_full_err = spectrum.rate[1] 
        ratefile = paths.productdir+paths.source_name+"_countrates.dat"        
        with open(ratefile,'a+') as file:
             file.write(str(rate_full)+ " "+str(rate_full_err)+" "+
                        str(rate_low)+ " "+str(rate_low_err)+" "+
                        str(rate_high)+ " "+str(rate_high_err)+" "+
                        str(RXTE_rate_low)+" "+str(RXTE_rate_low_err)+" "+
                        str(RXTE_rate_high)+" "+str(RXTE_rate_high_err)+"\n") 
        
        print("Fitting spectrum: ")
        #standard band for spectral fitting
        #spectrum.notice("0.5-10.0")
        spectrum.ignore("**-0.5")
        spectrum.ignore("10.0-**")          
        m1 = Model("tbabs*(nthComp+diskbb)")    
        m1.TBabs.nH = 0.1
        m1.TBabs.nH.frozen = False
        m1.nthComp.Gamma = [2.,.01,1.3,1.3,2.8,2.8]
        m1.nthComp.kT_e = 60.
        m1.nthComp.kT_e.frozen = True
        m1.nthComp.inp_type = 1.
        m1.diskbb.Tin = 1.
        m1.diskbb.norm = 1e3
        m1.nthComp.kT_bb = m1.diskbb.Tin
        m1.nthComp.kT_bb.frozen = False
        AllModels.show()
        Fit.renorm()
        Fit.perform()                
        plot_spectrum(index)
    
    Xset.closeLog()    
    logs.stop_logging()

def plot_spectrum(index):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import numpy as np
    import paths
    import logs
    
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    
    Plot.xAxis = "keV"
    Plot("eeufspec")
    xVals = np.array(Plot.x())
    yVals = np.array(Plot.y())
    #placehlder from RXTE, may not be necessary
    #for j in range (len(xVals)):
    #    yVals[j] = max(1e-4,np.array(Plot.y())[j])     
    xErrs = np.array(Plot.xErr())
    yErrs = np.array(Plot.yErr())    
    Plot("model")
    modx = np.array(Plot.x())
    modVals = np.array(Plot.model())
    
    fig, ((ax1), (ax2) ) = plt.subplots(2,1,figsize=(9.,7.5), gridspec_kw={'height_ratios': [3, 1]})    
    ax1.errorbar(xVals,yVals,xerr=xErrs,yerr=yErrs,color=colors[2],ls='none',fmt='o',zorder=1)
    ax1.plot(modx,modVals*modx**2,color=colors[3],linewidth=3.,zorder=2)     
    ax1.set_xlim([0.5,10.])
    ax1.set_ylim([max(0.9*np.min(yVals),0.01*np.max(yVals)),1.1*np.max(yVals)])
    ax1.set_xscale("log",base=10)
    ax1.set_yscale("log",base=10)    
    ax1.set_ylabel("Flux, keV$^{2}$ cm$^{-2}$ s$^{-1}$ keV$^{-1}$")    
    ax1.xaxis.set_major_formatter(plt.NullFormatter())    
    #plot residuals
    Plot("ratio")
    xVals = np.array(Plot.x())
    yVals = np.array(Plot.y())
    yErrs = np.array(Plot.yErr())
    res_axis = np.zeros(len(xVals))+1.    
    ax2.errorbar(xVals,yVals,xerr=xErrs,yerr=yErrs,color=colors[2],ls='none',fmt='o')
    ax2.plot(xVals,res_axis,linewidth=1.5,linestyle='dashed',color=colors[4])     
    ax2.set_xscale("log",base=10)
    ax2.set_xlabel("Energy (keV)",fontsize=20)
    ax2.set_ylabel("Ratio",fontsize=20)     
    plt.tight_layout()
    fig.subplots_adjust(hspace=0)  
    fig.savefig(paths.specplotir+"Spectrum_"+paths.obsid_list[index]+".pdf") 
    #delete spectra before moving on to the next
    plt.close(fig)
    AllData.clear()
    AllModels.clear()  
