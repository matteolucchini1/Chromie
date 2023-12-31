def extract_timing():
    import os
    import paths
    import logs
    logs.output("extract_timing")
   
    #clean up hue output files
    huepath=paths.productdir+"/*PC.dat"
    string="rm -r "+huepath
    os.system(string)
    
    for index in range(len(paths.obsid_list)):
        print("------------------------------------------------------------")
        print("Obsid:",paths.obsid_list[index])
        print("Extracting full band PSD")
        #events_to_PSD(0.3,12.,index)         
        print("Extracting low energy band PSD")
        #events_to_PSD(0.3,3.,index)         
        print("Extracting high energy band PSD")
        #events_to_PSD(3.,12.,index) 
        print("Computing lag frequency spectra")
        #events_to_lagf(index)
        print("Computing coherence")
       # events_to_coherence(index)
        print("Computing dynamical psd")
        events_to_dyn(index)
        
    logs.stop_logging()
    
def events_to_PSD(emin,emax,index):
    from stingray.gti import create_gti_from_condition, gti_border_bins, time_intervals_from_gtis, cross_two_gtis
    from stingray.utils import show_progress
    from stingray.fourier import avg_cs_from_events, avg_pds_from_events, poisson_level, get_average_ctrate
    from stingray import AveragedPowerspectrum, AveragedCrossspectrum, EventList
    import heasoftpy as hsp
    import numpy as np
    import paths
    import logs
    segment_size=512
    dt=1/64
    norm="frac"
    print("Computing PSD")
    
    fname = paths.obsdir[index]+"/ni"+paths.obsid_list[index]+"_0mpu7_cl.evt"
    events = EventList.read(fname, "hea")
    events.fname = fname
    energy_band = [emin,emax]
    events_filtered = events.filter_energy_range(energy_band)    
    plotname = str(emin)+"_"+str(emax)
    lightcurve_check(events,plotname,index)   
     
    duration_test = 0.
    for time in np.rollaxis(events_filtered.gti, 0):
        duration_test = np.max([time[1]-time[0],duration_test])
    
    if (duration_test > segment_size):
        psd = AveragedPowerspectrum.from_events(events_filtered, segment_size=segment_size, dt=dt,
                                        norm=norm, use_common_mean=True)
        #Calculate the mean count rate, Poisson noise, and rebin
        ctrate = get_average_ctrate(events_filtered.time, events_filtered.gti, segment_size)
        noise = poisson_level(norm, meanrate=ctrate)
        psd_reb = psd.rebin_log(0.01)

        #plot PSDs before and after rebinning
        plot_rebins(psd,psd_reb,noise,index,plotname)

        #calculate power colours
        get_power_colors(psd,noise,emin,emax)

        #save the psd to a dummy text file to import rebinned PSD to flx2xsp
        print("Saving PSD to file")
        save_path = paths.psdir+paths.obsid_list[index]+str(emin)+"_"+str(emax)+".dat"
        save_file = open(save_path, "w+")
        bin_width = psd_reb.df*psd_reb.k/2
        for i in range(len(psd_reb.freq)):
            save_file.write(str(psd_reb.freq[i]-bin_width[i])+" "+str(psd_reb.freq[i]+bin_width[i])+" "
                           +str(psd_reb.power[i]*bin_width[i])+" "+str(psd_reb.power_err[i]*bin_width[i])+"\n")
        save_file.close()

        #run flx2xsp to convert to fits file
        print("Converting PSD to fits")
        flx2xsp = hsp.HSPTask('ftflx2xsp')
        res2xsp = flx2xsp(infile=paths.psdir+paths.obsid_list[index]+str(emin)+"_"+str(emax)+".dat",
                          phafile=paths.psdir+paths.obsid_list[index]+"_"+str(emin)+"_"+str(emax)+".pha",
                          rspfile=paths.psdir+paths.obsid_list[index]+"_"+str(emin)+"_"+str(emax)+"_resp.rsp")
        if res2xsp.returncode != 0:
            print('Conversion successful')
        for o in res2xsp.output[:]:
            print(o)
        
    else:
        print("No GTIs long enough for obsid: ",paths.obsid_list[index])
        no_powercolors(emin,emax)


def plot_rebins(psd1,psd2,noise,index,plotname):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import paths
    import logs
    
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    
    print("Plotting binned and unbinned PSD")
    band1 = 0.0039
    band2 = 0.031
    band3 = 0.25
    band4 = 2
    band5 = 16
    fig, ((ax1, ax2)) = plt.subplots(1,2,figsize=(18.,6.)) 
    ax1.plot(psd1.freq,psd1.power,drawstyle="steps-mid",color=colors[1],label="PSD")
    ax1.plot(psd2.freq,psd2.power,drawstyle="steps-mid",color=colors[3],label="Rebinned PSD",linewidth=3)
    ax1.axhline(noise, ls=":",label="Poisson noise level",color=colors[4],linewidth=3)
    ax1.loglog()
    ax1.set_xlabel("Frequency (Hz)",fontsize=20)
    ax1.set_ylabel(r"$\mathrm{(rms / mean)^2 Hz^{-1}}$",fontsize=20);
    ax1.legend(loc='lower left')    
    ax2.plot(psd1.freq,(psd1.power-noise)*psd1.freq,drawstyle="steps-mid",
             color=colors[1],label="PSD")
    ax2.plot(psd2.freq,(psd2.power-noise)*psd2.freq,drawstyle="steps-mid",
             color=colors[3],label="Rebinned PSD",linewidth=3)
    ax2.axvline(band1, ls=":",color=colors[4],linewidth=2)
    ax2.axvline(band2, ls=":",color=colors[4],linewidth=2)
    ax2.axvline(band3, ls=":",color=colors[4],linewidth=2)
    ax2.axvline(band4, ls=":",color=colors[4],linewidth=2)
    ax2.axvline(band5, ls=":",color=colors[4],linewidth=2)
    ax2.loglog()
    ax2.set_xlabel("Frequency (Hz)",fontsize=20)
    ax2.set_ylabel(r"$\mathrm{(rms / mean)^2}$",fontsize=20);
    ax2.legend(loc='lower right')    
    plt.tight_layout()
    fig.savefig(paths.psdplotir+"PSD_"+paths.obsid_list[index]+"_"+plotname+".pdf")
    plt.close(fig)
    print("PSD plot done")  

def get_power_colors(psd,noise,emin,emax):
    import numpy as np
    import paths
    import logs
    #note: pass the UNBINNED power spectrum here, there are fewer issues with bin widths 
    #overlapping with frequency bands
    #this code is taken from the Chromos RXTE pipeline 
    frequency_bands = [1/256.,1/32.,0.25,2.0,16.0]
    variances = []
    variance_errors = []
    index_frequency_bands = []
    # Convert frequency bands to index values from in the frequency list
    for fb in frequency_bands:
        index = min(range(len(psd.freq)), key=lambda i: abs(psd.freq[i]-fb))
        index_frequency_bands.append([index])        
    # Group indexes into sets of style [low, high)
    for i, e in enumerate(index_frequency_bands[:-1]):
        e.append(index_frequency_bands[i+1][0]-1)
    del index_frequency_bands[-1]
    # Integrate the power spectra within the frequency bands
    bin_width = psd.df

    for e in index_frequency_bands:
        variance = bin_width*sum(psd.power[e[0]:e[1]]-noise)
        variances.append(variance)
        # Calculate errors on the variance
        # (see appendix Heil, Vaughan & Uttley 2012)
        # M refers to the number of segments
        one_over_sqrt_M = 1/float(psd.m)
        prop_std = sum((psd.power[e[0]:e[1]]-noise)**2)
        variance_error = bin_width*one_over_sqrt_M*np.sqrt(prop_std)
        variance_errors.append(variance_error)
        
    pc1 = variances[2]/float(variances[0])
    pc2 = variances[1]/float(variances[3])

    pc1_error = np.sqrt((variance_errors[2]/float(variances[2]))**2 +
                        (variance_errors[0]/float(variances[0]))**2)*pc1
    pc2_error = np.sqrt((variance_errors[1]/float(variances[1]))**2 +
                        (variance_errors[3]/float(variances[3]))**2)*pc2
    colorfile = paths.productdir+paths.source_name+"_"+str(emin)+"_"+str(emax)+"_PC.dat"
    with open(colorfile,'a+') as file:
        file.write(str(pc1)+" "+str(pc1_error)+" "+str(pc2)+" "+str(pc2_error)+"\n")

def no_powercolors(emin,emax):    
    import paths
    import logs
    colorfile = paths.productdir+paths.source_name+"_"+str(emin)+"_"+str(emax)+"_PC.dat"
    #note: these are set to nan so that the plots will just skip them
    with open(colorfile,'a+') as file:
        file.write("Nan NaN NaN NaN \n")

def events_to_lagf(index):
    from stingray.gti import create_gti_from_condition, gti_border_bins, time_intervals_from_gtis, cross_two_gtis
    from stingray.utils import show_progress
    from stingray.fourier import avg_cs_from_events, avg_pds_from_events, poisson_level, get_average_ctrate
    from stingray import AveragedPowerspectrum, AveragedCrossspectrum, EventList
    import numpy as np
    import paths
    import logs
   
    band1 = [0.3,1.0]
    band2 = [2.0,4.0]
    #tbd - figure out the optimal band here, reference band is the reverberation band I think 
    band3 = [6.,7.0] 
    fname = paths.obsdir[index]+"/ni"+paths.obsid_list[index]+"_0mpu7_cl.evt"
    events = EventList.read(fname, "hea")
    events.fname = fname    
    ref_band = band2
    reverb_band_soft = band1
    reverb_band_Fe = band3
    events_ref = events.filter_energy_range(ref_band)
    events_soft = events.filter_energy_range(reverb_band_soft) 
    events_Fe = events.filter_energy_range(reverb_band_Fe)       
    cs_soft = AveragedCrossspectrum.from_events(events_ref, events_soft, segment_size=2., dt=0.005, norm="frac")
    cs_soft = cs_soft.rebin_log(0.1)
    cs_Fe = AveragedCrossspectrum.from_events(events_ref, events_Fe, segment_size=2., dt=0.005, norm="frac")
    cs_Fe = cs_Fe.rebin_log(0.1)
    lag_soft, lag_soft_e = cs_soft.time_lag()
    lag_Fe, lag_Fe_e = cs_Fe.time_lag()
    plot_lags(cs_soft.freq,lag_soft,lag_soft_e,lag_Fe,lag_Fe_e,index)
    
def plot_lags(freq,lag1,lag1_e,lag2,lag2_e,index):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import paths
    import logs
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    
    print("Plotting lag-frequency: ")
    fig, (ax1) = plt.subplots(1,1,figsize=(9.,6.)) 
    ax1.errorbar(freq,lag1,yerr=lag1_e,color=colors[3],label="0.3-1/2-4 keV",drawstyle="steps-mid",lw=3,zorder=2)
    ax1.errorbar(freq,lag2,yerr=lag2_e,color=colors[1],label="6.0-7.0/2-4 keV",drawstyle="steps-mid",lw=3,zorder=1)
    ax1.axhline(0, ls=":",color=colors[4],linewidth=3)
    ax1.set_xlabel("Frequency (Hz)",fontsize=20)
    ax1.set_ylabel("Lag (s)",fontsize=20)
    ax1.set_xscale("log",base=10)
    ax1.legend(loc="upper right")
    ax1.set_xlim([0.45,40.])
    plt.tight_layout()
    fig.savefig(paths.lagplotir+"LagF_"+paths.obsid_list[index]+".pdf")
    plt.close(fig)
    print("Lag-frequency plot done") 

def events_to_coherence(index):
    from stingray.gti import create_gti_from_condition, gti_border_bins, time_intervals_from_gtis, cross_two_gtis
    from stingray.utils import show_progress
    from stingray.fourier import avg_cs_from_events, avg_pds_from_events, poisson_level, get_average_ctrate
    from stingray import AveragedPowerspectrum, AveragedCrossspectrum, EventList
    import numpy as np
    import paths
    import logs
   
    band1 = [0.3,1.0]
    band2 = [2.0,4.0]
    #tbd - figure out the optimal band here, reference band is the reverberation band I think 
    band3 = [6.,7.0] 
    fname = paths.obsdir[index]+"/ni"+paths.obsid_list[index]+"_0mpu7_cl.evt"
    events = EventList.read(fname, "hea")
    events.fname = fname    
    ref_band = band2
    reverb_band_soft = band1
    reverb_band_Fe = band3
    events_ref = events.filter_energy_range(ref_band)
    events_soft = events.filter_energy_range(reverb_band_soft) 
    events_Fe = events.filter_energy_range(reverb_band_Fe)       
    cs_soft = AveragedCrossspectrum.from_events(events_ref, events_soft, segment_size=10., dt=0.005, norm="frac")
    cs_soft = cs_soft.rebin_log(0.1)
    cs_Fe = AveragedCrossspectrum.from_events(events_ref, events_Fe, segment_size=10., dt=0.005, norm="frac")
    cs_Fe = cs_Fe.rebin_log(0.1)
    coh_soft, coh_soft_e = cs_soft.coherence()
    coh_Fe, coh_Fe_e = cs_Fe.coherence()
    plot_coherence(cs_soft.freq,coh_soft,coh_soft_e,coh_Fe,coh_Fe_e,index)

def plot_coherence(freq,coh1,coh1_e,coh2,coh2_e,index):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import paths
    import logs
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    
    print("Plotting coherence: ")
    fig, (ax1) = plt.subplots(1,1,figsize=(9.,6.)) 
    ax1.errorbar(freq,coh1,yerr=coh1_e,color=colors[3],label="0.3-1/2-4 keV",drawstyle="steps-mid",lw=3,zorder=2)
    ax1.errorbar(freq,coh2,yerr=coh2_e,color=colors[1],label="6.0-7.0/2-4 keV",drawstyle="steps-mid",lw=3,zorder=1)
    ax1.axhline(1, ls=":",color=colors[4],linewidth=3)
    ax1.set_xlabel("Frequency (Hz)",fontsize=20)
    ax1.set_ylabel("Coherence",fontsize=20)
    ax1.set_xscale("log",base=10)
    ax1.set_yscale("log",base=10)
    ax1.legend(loc="lower left")
    ax1.set_xlim([0.09,110.])
    plt.tight_layout()
    fig.savefig(paths.lagplotir+"Coh_"+paths.obsid_list[index]+".pdf")
    plt.close(fig)
    print("Coherence plot done") 

def events_to_dyn(index):
    from stingray.gti import create_gti_from_condition, gti_border_bins, time_intervals_from_gtis, cross_two_gtis
    from stingray.utils import show_progress
    from stingray.fourier import avg_cs_from_events, avg_pds_from_events, poisson_level, get_average_ctrate
    from stingray import AveragedPowerspectrum, AveragedCrossspectrum, EventList, DynamicalPowerspectrum
    import numpy as np
    import paths
    import logs  
 
    norm="frac"
    fname = paths.obsdir[index]+"/ni"+paths.obsid_list[index]+"_0mpu7_cl.evt"
    events = EventList.read(fname, "hea")
    events.fname = fname
    time_resolution = 150
    ctrate = get_average_ctrate(events.time, events.gti, time_resolution)
    noise = poisson_level(norm, meanrate=ctrate)
    #this ensures that the GTIs are large enough for the time resolution    
    duration_test = 0.
    for time in np.rollaxis(events.gti, 0):
        duration_test = np.max([time[1]-time[0],duration_test])
    if (duration_test < time_resolution):
        time_resolution = duration_test
    #to get the dynamical psd we need to turn event files into a lightcurve
    lightcurve_full = events.to_lc(dt=0.025)
    lightcurve_full.apply_gtis()
    dyn_psd = DynamicalPowerspectrum(lightcurve_full, segment_size=time_resolution)
    dyn_psd = dyn_psd.rebin_frequency(df_new=0.1, method="average")
    plot_dyn(index,dyn_psd,noise)

def plot_dyn(index,psd,noise):   
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
    print("Plotting dynamical PSD: ")  
     
    #tbd: move this to a separate function
    psd_plot = np.zeros((len(psd.freq), len(psd.time)))  
    for i in range(len(psd.freq)):
        for j in range(len(psd.time)):
            psd_plot[i][j] = (psd.dyn_ps[i][j]-noise)*psd.freq[i]    
    color_max = np.log10(1.05*psd_plot.max())
    color_min = color_max-1.5
        
    fig, (ax1) = plt.subplots(1,1,figsize=(9.,6.)) 
    extent = min(psd.time), max(psd.time), min(psd.freq), max(psd.freq)
    img = ax1.imshow(np.log10(psd_plot), aspect="auto", origin="lower", interpolation="none", 
                     extent=extent, vmax=color_max, vmin=color_min, cmap = "magma")
    ax1.set_xlabel('Time (s)',fontsize="20")
    ax1.set_yscale("log",base=10)
    ax1.set_ylabel('Frequency (Hz)',fontsize="20")
    plt.colorbar(img, ax=ax1,label='Power')
    plt.tight_layout()
    fig.savefig(paths.psdplotir+"Dynamic_"+paths.obsid_list[index]+".pdf")
    plt.close(fig)    
    print("Dynamical PSD plot done")  

def lightcurve_check(events,plotname,index):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import paths
    import logs
    
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    
    print("Checking Lightcurve")
    # Create light curve and apply GTIs
    lc_raw = events.to_lc(dt=1/64)
    lc_raw.apply_gtis()
    fig, (ax1) = plt.subplots(1,1,figsize=(9.,6.)) 
    ax1.plot(lc_raw.time, lc_raw.counts, color=colors[3], label="Raw")
    #ax1.plot(lc.time, lc.counts, color=colors[3], label="Cleaned",linewidth=3)
    ax1.set_xlabel(f"Time (s from {events.mjdref})",fontsize=20)
    ax1.set_ylabel(f"Counts/bin",fontsize=20)
    fig.savefig(paths.lcplotir+"LC_"+paths.obsid_list[index]+"_"+plotname+".pdf") 
    plt.close(fig)
    print("Lightcurve plot done")
