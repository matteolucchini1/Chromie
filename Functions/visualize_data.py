def visualize_data():
    import numpy as np
    import paths
    import logs       
    logs.output("visualize_data")
    print("------------------------------------------------------------")
    print("Visualizing data: ")
    
    print("Recovering count rates:")    
    ratefile = paths.productdir+paths.source_name+"_countrates.dat" 
    rates = np.genfromtxt(ratefile,dtype=float)
    rate_full = rates.T[0]
    rate_full_err = rates.T[1]
    NICER_rate_soft = rates.T[2]
    NICER_rate_soft_err = rates.T[3]
    NICER_rate_hard = rates.T[4]
    NICER_rate_hard_err = rates.T[5]
    RXTE_rate_low = rates.T[6]
    RXTE_rate_low_err = rates.T[7]
    RXTE_rate_high = rates.T[8]
    RXTE_rate_high_err = rates.T[9]
    #y axis: always full rate, 0.5-10 
    #x axis: 0.3-3 vs 3-10 and 3-6 vs 6-10
    NICER_hardness = NICER_rate_hard/NICER_rate_soft
    RXTE_hardness = RXTE_rate_high/RXTE_rate_low    
    NICER_hardness_err = NICER_hardness*np.sqrt((NICER_rate_soft_err/NICER_rate_soft)**2+
                                                                   (NICER_rate_hard_err/NICER_rate_hard)**2)
    RXTE_hardness_err = RXTE_hardness*np.sqrt((RXTE_rate_low_err/RXTE_rate_low)**2+
                                                                (RXTE_rate_high_err/RXTE_rate_high)**2) 
    plot_hid(rate_full,rate_full_err,NICER_hardness,NICER_hardness_err,RXTE_hardness,RXTE_hardness_err)
    
    print("Recovering power colours and hue: ")
    emin = "0.3"
    emax = "3.0"
    hue_low,hue_low_err = calculate_hue(emin,emax)
    colorfile = paths.productdir+paths.source_name+"_"+emin+"_"+emax+"_PC.dat"
    colors_low = np.genfromtxt(colorfile,dtype=float)
    emin = "3.0"
    emax = "12.0"
    hue_high,hue_high_err = calculate_hue(emin,emax)
    colorfile = paths.productdir+paths.source_name+"_"+emin+"_"+emax+"_PC.dat"
    colors_high = np.genfromtxt(colorfile,dtype=float)
    emin = "0.3"
    emax = "12.0"
    hue_full,hue_full_err = calculate_hue(emin,emax)
    colorfile = paths.productdir+paths.source_name+"_"+emin+"_"+emax+"_PC.dat"
    colors_all = np.genfromtxt(colorfile,dtype=float)
    #tbd: check here for small error bars
    plot_powercolours(colors_low,colors_high,colors_all)
       
    print("Recovering dates: ")
    datefile = paths.productdir+paths.source_name+"_dates.dat"
    dates = np.genfromtxt(datefile,dtype=float)  
    
    plot_lightcurve(dates,rate_full,rate_full_err)  
    plot_hue(dates,hue_low,hue_low_err,hue_high,hue_high_err,hue_full,hue_full_err)
    plot_evolution(dates,hue_full,hue_full_err,NICER_hardness,NICER_hardness_err,"NICER")
    plot_evolution(dates,hue_high,hue_high_err,RXTE_hardness,RXTE_hardness_err,"RXTE")
    plot_huevshardness(hue_full,hue_full_err,NICER_hardness,NICER_hardness_err,"NICER")
    plot_huevshardness(hue_high,hue_high_err,RXTE_hardness,RXTE_hardness_err,"RXTE")    
    
    logs.stop_logging()

def plot_hid(rate,rate_err,hr_1,hr_1_err,hr_2,hr_2_err):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import os
    import numpy as np
    import paths
    import logs
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    print("Plotting HID: ")
    fig, ((ax1), (ax2) ) = plt.subplots(1,2,figsize=(18.,6.))    
    ax1.errorbar(hr_1,rate,xerr=hr_1_err,yerr=rate_err,
                 fmt='o',ms=10,color=colors[3])
    ax1.set_yscale("log",base=10)
    ax1.set_ylabel('0.3-10 keV counts/s',fontsize=20)
    ax1.set_xlabel('3-10 keV/0.3-3 keV counts/s',fontsize=20)
    
    ax2.errorbar(hr_2,rate,xerr=hr_2_err,yerr=rate_err,
                 fmt='o',ms=10,color=colors[3])
    ax2.set_yscale("log",base=10)
    ax2.yaxis.set_major_formatter(plt.NullFormatter())  
    ax2.yaxis.set_minor_formatter(plt.NullFormatter())  
    ax2.set_xlabel('6-12 keV/3-6 keV counts/s',fontsize=20)
    plt.tight_layout()
    fig.subplots_adjust(wspace=0)  
    fig.savefig(paths.plotdir+"HID_"+paths.source_name+".pdf") 
    plt.close(fig)

def plot_powercolours(list_1,list_2,list_3):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import os
    import numpy as np
    import paths
    import logs
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})       
    print("Plotting powercolours: ")   

    PC1_1,PC1_1_err,PC2_1,PC2_1_err = filter_powercolours(list_1)  
    PC1_2,PC1_2_err,PC2_2,PC2_2_err = filter_powercolours(list_2) 
    PC1_3,PC1_3_err,PC2_3,PC2_3_err = filter_powercolours(list_3)   
     
    fig, (ax1) = plt.subplots(1,1,figsize=(9.,6.))           
    ax1.errorbar(PC1_1,PC2_1,xerr=PC1_1_err,yerr=PC2_1_err,fmt='o',ms=10,color=colors[1],label="0.3-3 keV")  
    ax1.errorbar(PC1_2,PC2_2,xerr=PC1_2_err,yerr=PC2_2_err,fmt='o',ms=10,color=colors[2],label="3-12 keV")
    ax1.errorbar(PC1_3,PC2_3,xerr=PC1_3_err,yerr=PC2_3_err,fmt='o',ms=10,color=colors[3],label="0.3-12 keV")
    ax1.scatter(4.51920, 0.453724,marker='X',color='black',s=400,zorder=20)
    ax1.set_xscale("log",base=10)
    ax1.set_yscale("log",base=10)
    ax1.set_xlim([0.0011,200.0])
    ax1.set_ylim([0.01,250.0])
    ax1.set_xlabel("PC1",fontsize=20)
    ax1.set_ylabel("PC2",fontsize=20)
    ax1.legend(loc="best")
    plt.tight_layout()
    fig.savefig(paths.plotdir+"Powercolours_"+paths.source_name+".pdf")
    plt.close(fig) 

def fiter_powercolours(colors):
    import numpy as np
    import paths
    import logs  
    #this function includes only powercolours with sigma 3 times smaller than their magnitude  
    PC1=[]
    PC1_err=[]
    PC2=[]
    PC2_err=[]
    for i in range(len(colors.T[0])):
        if (colors.T[0][i]-3.*colors.T[1][i]) > 0 and (colors.T[2][i]-3.*colors.T[3][i]) > 0:
            PC1.append(colors.T[0][i])
            PC1_err.append(colors.T[1][i]])
            PC2.append(colors.T[2][i]) 
            PC2_err.append(colors.T[3][i]])      
    return PC1,PC1_err,PC2,PC2_err

def plot_lightcurve(dates,counts,counts_err):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import os
    import numpy as np
    import paths
    import logs
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    print("Plotting lightcurve: ")
    fig, (ax1) = plt.subplots(1,1,figsize=(9.,6.))  
    ax1.errorbar(dates,counts,yerr=counts_err,fmt='o',ms=10,color=colors[3])
    ax1.set_yscale("log",base=10)
    ax1.set_xlabel("Date (MJD)",fontsize=20)
    ax1.set_ylabel("0.3-10 keV counts/s",fontsize=20)
    plt.tight_layout()
    fig.savefig(paths.plotdir+"Lightcurve_"+paths.source_name+".pdf")
    plt.close(fig)

def plot_hue(dates,hue_1,hue_1_err,hue_2,hue_2_err,hue_3,hue_3_err):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import os
    import numpy as np
    import paths
    import logs
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    print("Plotting hues: ")
    fig, (ax1) = plt.subplots(1,1,figsize=(9.,6.))  
    ax1.errorbar(dates,hue_1,yerr=hue_1_err,fmt='o',ms=10,color=colors[1],label="0.3-3 keV")
    ax1.errorbar(dates,hue_2,yerr=hue_2_err,fmt='o',ms=10,color=colors[2],label="3-12 keV")
    ax1.errorbar(dates,hue_3,yerr=hue_3_err,fmt='o',ms=10,color=colors[3],label="0.3-12 keV")
    ax1.set_xlabel("Date (MJD)",fontsize=20)
    ax1.set_ylabel("Hue (deg)",fontsize=20)    
    ax1.legend(loc="best")
    plt.tight_layout()
    fig.savefig(paths.plotdir+"Hue_"+paths.source_name+".pdf")
    plt.close(fig)
    
def plot_evolution(dates,hue,hue_err,hardness,hardness_err,string):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import os
    import numpy as np
    import paths
    import logs
    colors = ['#02d8e9','#21b1ff','#ff218c','#ff81c0','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    print("Plotting hues+hardness: ")
    fig, ax1 = plt.subplots(figsize=(9.,6.)) 
    ax1.errorbar(dates,hue,yerr=hue_err,fmt='o',ms=10,color=colors[1])
    ax1.set_ylabel('Power spectral hue (deg)',fontsize=24)
    ax1.set_xlabel('Time since start (days)',fontsize=24)
    ax1.set_xlabel("Date (MJD)",fontsize=20)
    ax1.set_ylabel("Hue (deg)",fontsize=20)    
    ax2 = ax1.twinx()
    ax2.errorbar(dates,hardness,yerr=hardness_err,fmt='o',ms=10,color=colors[2])
    ax2.set_ylabel('Spectral hardness',fontsize=20)    
    ax2.spines['left'].set_color(colors[1])
    ax1.tick_params(axis='y', colors=colors[1])
    ax1.yaxis.label.set_color(colors[1])
    ax2.spines['right'].set_color(colors[2])
    ax2.tick_params(axis='y', colors=colors[2])
    ax2.yaxis.label.set_color(colors[2])
    plt.tight_layout()
    fig.savefig(paths.plotdir+"HueAndHardness_"+string+"_"+paths.source_name+".pdf")
    plt.close(fig)

def plot_huevshardness(hue,hue_err,hardness,hardness_err,string):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rc, rcParams
    import os
    import numpy as np
    import paths
    import logs
    colors=['#9c394a','#b4c5f6','#7ba4f6','#29318b','#62737b']
    rc('text',usetex=True)
    rc('font',**{'family':'serif','serif':['Computer Modern']})
    plt.rcParams.update({'font.size': 18})
    print("Plotting hue vs hardness: ")
    fig, (ax1) = plt.subplots(1,1,figsize=(9.,6.))    
    ax1.errorbar(hue,hardness,xerr=hue_err,yerr=hardness_err,
                 fmt='o',ms=10,color=colors[3])
    ax1.set_xlabel('Hue (Deg)',fontsize=20)
    ax1.set_ylabel('Hardness',fontsize=20)
    plt.tight_layout()
    fig.subplots_adjust(wspace=0)  
    fig.savefig(paths.plotdir+"HueVsHR_"+string+"_"+paths.source_name+".pdf") 
    plt.close(fig)
    
def calculate_hue(emin,emax):
    import numpy as np
    from random import gauss
    import os
    import paths
    import logs
    colorfile = paths.productdir+paths.source_name+"_"+emin+"_"+emax+"_PC.dat"
    colour_contents=np.genfromtxt(colorfile,dtype=float)    
    hue = np.zeros(len(paths.obsid_list))
    hue_err = np.zeros(len(paths.obsid_list))
    
    for index in range(len(paths.obsid_list)):
        hue_x = np.log10(colour_contents.T[0][index])-np.log10(4.51920)
        hue_y = -np.log10(colour_contents.T[2][index])+np.log10(0.453724)
        hue[index] = np.arctan2(hue_y,hue_x)*180/3.14+135    
        #errors are computed numerically by drawing from gaussian distributions for the power colours
        #because I hate doing this analytically with atan2
        hue_gen = []
        for i in range(1,1000):
            random_x = gauss(colour_contents.T[0][index],colour_contents.T[1][index])
            random_hue_x = np.log10(np.max([random_x,1e-5]))-np.log10(4.51920)
            random_y = gauss(colour_contents.T[2][index],colour_contents.T[3][index])
            random_hue_y = np.log10(np.max([random_y,1e-5]))+np.log10(0.453724)
            hue_gen.append(np.arctan2(random_hue_x,random_hue_y)*180/3.14+135) 
        hue_err[index] = np.std(hue_gen,axis=0)            
    
    return hue,hue_err
