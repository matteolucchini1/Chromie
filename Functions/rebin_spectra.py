def rebin_spectra():
    import os
    import paths
    import logs
    import subprocess
    logs.output("rebin_spectra")
    print("Rebinning spectra: ")

    for index in range(len(paths.obsid_list)):
        print("------------------------------------------------------------------------------------------")
        print("Over-sampling the instrument resolution: ")
        spectrum_file=paths.specdir+paths.obsid_list[index]+".pha"
        oversample_file=paths.specdir+paths.obsid_list[index]+"_ovs.pha"
        rebin_file=paths.specdir+paths.obsid_list[index]+"_rebin.pha"
        resolution_oversample_string = "grppha "+spectrum_file+" !"+oversample_file+" \"reset quality & bad 0-29 1200-1500 & group nicer_channels_to_group.txt & exit\"\n"
        #note: the grppha log info is added by hand here because grppha is annoying in heasoftpy   
        os.system(resolution_oversample_string)     
        grp_output = subprocess.check_output(resolution_oversample_string, shell=True,text=True)
        logpath = paths.logdir+"rebin_spectra.log"
        print(grp_output)
        print("Rebinning to 25 counts per bin: ")
        jsgroup(oversample_file,25.,rebin_file)
        print("Final product: " + rebin_file)
        
    logs.stop_logging()
   
    
def jsgroup(rebin_file,min_counts,mincounts_file):
    #This code is Jack Steiner's, I take zero credit for this 
    import os
    from astropy.io import fits
    from astropy.io.fits import getdata,update
    from astropy.table import Table
    import numpy as np
    import paths
    import logs
    logs.output("rebin_spectra")
    hdu = fits.open(rebin_file)
    spectrum = hdu[1].data
    exposure = hdu[1].header['EXPOSURE']
    columns = spectrum.columns
    quality = spectrum['QUALITY']
    grouping = spectrum['GROUPING']
    if 'RATE' in columns.names:
        counts = spectrum['RATE'] * exposure
    elif 'COUNTS' in columns.names:
        counts =  spectrum['COUNTS']
    else:
        print('No "RATE" or "COUNTS" column found. Exiting program.')
        exit()
    print('Total counts between 0.3 and 12 keV is:', np.sum(counts[30:1200]))
    if np.sum(counts[30:1200]) < min_counts:    
        print('Not enough counts in spectrum to fill a single bin with minimum counts.')
        exit()
    
    print('Find starting bins of current groups')
    group_start = np.where(grouping[30:1200]==1)[0] + 30 # add 30 because we start the np.where statement at 30
    total_groups = len(group_start)
    print('Current number of groups is:', total_groups)
    counts_per_group = np.zeros(total_groups,dtype=int)
    print('Calculating counts per group')
    for i in range(total_groups-1):
        counts_per_group[i] = np.sum(counts[group_start[i]:group_start[i+1]])
        #print(i+1, group_start[i], group_start[i+1]-1, counts_per_group[i])
    counts_per_group[total_groups-1] = np.sum(counts[group_start[total_groups-1]:1200])
    print(total_groups, group_start[total_groups-1], '1199', counts_per_group[total_groups-1])
    print('Rebinning for minimum of', min_counts,'per bin')

    i = 0  # tracks group number
    last_complete_group = 0 # tracks latest group with min_counts or more counts
    total_counts = 0 # tracks total number of counts in combined groups
    number_of_groups = 0 # tracks current number of combined groups
    not_the_end = True # Flag to check if final group has been reached

    while not_the_end:
        total_counts = total_counts + counts_per_group[i]
        number_of_groups = number_of_groups + 1 
        if total_counts < min_counts:
            if number_of_groups == 1:
                grouping[group_start[i]] = 1
            else:
                grouping[group_start[i]] = -1
            #print(i, group_start[i], number_of_groups, counts_per_group[i], total_counts, grouping[group_start[i]])
            i = i + 1
        if total_counts >= min_counts:
            if number_of_groups == 1:
                grouping[group_start[i]] = 1
            else:
                grouping[group_start[i]] = -1
            #print(i, group_start[i], number_of_groups, counts_per_group[i], total_counts, grouping[group_start[i]])
            total_counts =  0 
            number_of_groups =  0 
            last_complete_group = i
            i = i + 1
        if i >= total_groups:
            not_the_end = False
    #print('out of while loop')
    #print('last_complete_group',last_complete_group)
    #print('Last complete group (with '+str(min_counts)+' counts) is: '+str(last_complete_group)+', which ends at channel:',group_start[last_complete_group+1]-1 )
    #print('Setting channels',group_start[last_complete_group+1],'to 1200 to bad (quality flag 2)')
    # this line is what I added to Jeroen's version, when all the groups are complete
    if last_complete_group+1<len(group_start):
        quality[group_start[last_complete_group+1]:1200] = 2
    print('Writing spectrum:', mincounts_file )
    hdu.writeto(mincounts_file,overwrite=True)
    print('Done - happy fitting!')
    #return
