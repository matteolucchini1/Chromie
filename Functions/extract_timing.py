def extract_timing():
    import os
    import paths
    import logs
    logs.output("extract_psd")
   
    #clean up hue output files
    huepath=paths.productdir+"/*PC.dat"
    string="rm -r "+huepath
    os.system(string)
    
    for index in range(len(paths.obsid_list)):
        print("------------------------------------------------------------")
        print("Obsid:",paths.obsid_list[index])
        print("Extracting full band PSD")
        events_to_PSD(0.3,12.,index)         
        print("Extracting low energy band PSD")
        events_to_PSD(0.3,3.,index)         
        print("Extracting high energy band PSD")
        events_to_PSD(3.,12.,index) 
        
    logs.stop_logging()
    
def events_to_PSD(emin,emax,index):
    from stingray.gti import create_gti_from_condition, gti_border_bins, time_intervals_from_gtis, cross_two_gtis
    from stingray.utils import show_progress
    from stingray.fourier import avg_cs_from_events, avg_pds_from_events, poisson_level, get_average_ctrate
    from stingray import AveragedPowerspectrum, AveragedCrossspectrum, EventList
    from stingray.modeling.parameterestimation import PSDLogLikelihood
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
    import paths
    import logs
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
        file.write("Nan NaN NaN NaN \n")

def no_powercolors(emin,emax):    
    import paths
    import logs
    colorfile = paths.productdir+paths.source_name+"_"+str(emin)+"_"+str(emax)+"_PC.dat"
    #note: these are set to nan so that the plots will just skip them
    with open(colorfile,'a+') as file:
        file.write(str(NaN)+" "+str(NaN)+" "+str(NaN)+" "+str(NaN)+"\n")

def lightcurve_check(events,plotname,index):
    import paths
    import logs
    print("Checking GTIs")
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
