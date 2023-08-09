def observation_times():
    from astropy.io import fits
    from astropy.time import Time
    import os
    import paths
    import logs
    logs.output("observation_times")
    print("------------------------------------------------------------")
    print("Grabbing observation times")
    
    #clean up date output files
    datepath=paths.productdir+"*dates.dat"
    string="rm -r "+datepath
    os.system(string)
    
    for index in range(len(paths.obsid_list)):
        spectrum_path=paths.specdir+paths.obsid_list[index]+".pha"
        spectrum_open = fits.open(spectrum_path)
        date_obs = spectrum_open[0].header['DATE-OBS']
        time_obs = Time(date_obs)
        mjd_obs = time_obs.mjd   
        datefile = paths.productdir+paths.source_name+"_dates.dat"
        with open(datefile,'a+') as file:
            file.write(str(mjd_obs)+"\n")    
    
    logs.stop_logging()
    
