def run_nicerl2(mkf):
    import heasoftpy as hsp
    import os
    import paths
    import logs

    logs.output("nicerl2")
    full_cleanup = True
    print("Runninc nicerl2: ")
    
    for index in range(len(paths.obsid_list)):
        nicerl2 = hsp.HSPTask('nicerl2')
        nicerl2.clobber="yes"
        nicerl2.autoscreen="yes"
        nicerl2.detlist="launch,-14,-34"
        # add the KP values to the mkf file during nicerl2 processing
        nicerl2.geomag_path="/home/matteo/Software/Geomag/"
        nicerl2.geomag_columns="kp_noaa.fits(KP)"
        print("------------------------------------------------------------")
        resl2 = nicerl2(indir=paths.obsdir[index], noprompt=True, cldir=paths.outdir[index], 
                        mkfile=mkf[index])
        if resl2.returncode != 0:
            print('\n')
        for o in resl2.output[:]:
            print(o)
        if (full_cleanup==True):
            cleanup_path = paths.outdir[index]
            print("Cleaning up evt files:")
            os.chdir(paths.outdir[index])
            print("Path test:",paths.outdir[index])
            string = "rm -r *tmp*"
            os.system(string)
            for j in range(0,7):
                cwd = os.getcwd()
                string = "rm -r *"+str(j)+"_ufa.evt"
                os.system(string)
            print("Cleaned up in path:",cwd)

    logs.stop_logging()

#tbd here: add option to clean up level 1 files
