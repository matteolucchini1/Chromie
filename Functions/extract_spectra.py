def extract_spectra(mkf):
    import heasoftpy as hsp
    import paths
    import logs
    logs.output("nicerl3-spect")
    full_cleanup = True
    print("Extracting spectra: ")
    
    for index in range(len(paths.obsid_list)):
        nicerl3 = hsp.HSPTask('nicerl3-spect')
        nicerl3.clobber="yes"
        nicerl3.detlist="launch,-14,-34"
        nicerl3.grouptype="none"
        #add the KP values to the mkf file during nicerl3 processing
        nicerl3.geomag_path=paths.geomag_path
        nicerl3.geomag_columns="kp_noaa.fits(KP)"
        print("------------------------------------------------------------")
        resl3 = nicerl3(indir=paths.obsdir[index], noprompt=True, cldir=paths.outdir[index], 
                        phafile=paths.specdir+paths.obsid_list[index]+".pha",
                        arffile=paths.specdir+paths.obsid_list[index]+"_arf.pha",
                        rmffile=paths.specdir+paths.obsid_list[index]+"_rmf.pha",
                        bkgfile=paths.specdir+paths.obsid_list[index]+"_bkg.pha",
                        bkgmodeltype="3c50",mkfile=mkf[index])
        if resl3.returncode != 0:
            print('\n')
        for o in resl3.output[:]:
            print(o)

    logs.stop_logging()


