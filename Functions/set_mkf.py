#this needs to be a list of mkf files so that it can be accessed later
def set_mkf():
    import os
    import os.path
    import paths  
    import logs
    logs.output("mkf")
    print("Setting up mkf file: ")
    mkf_arr=[]
    for index in range(len(paths.obsid_list)):
        # copy the mkf file from the input directory to the outdir
        mkf = os.path.join(paths.obsdir[index],'auxil',f'ni{paths.obsid_list[index]}.mkf')
        if os.path.exists(mkf):
            # see if mkf is gzipped    
            cmd = f'cp {mkf} {paths.outdir[index]}/.'
            stat=os.system(cmd)
            mkf = os.path.join(paths.outdir[index], os.path.split(mkf)[1])
            #print(f'Setting mkf file to {mkf}')
        elif os.path.exists(mkf+'.gz'):
            #copy gzipped mkf, then unzip it     
            cmd = f'cp {mkf}.gz {paths.outdir[index]}/.'
            os.system(cmd)
            mkf = os.path.join(paths.outdir[index], os.path.split(mkf)[1])
            cmd = f'gunzip -f {mkf}.gz'
            stat=os.system(cmd)
            #print(f'Setting mkf file to {mkf}')
        else: 
            print('ERROR mkf not found, check obsid ',paths.obsid_list[index])
        cmd = f'chmod u+w {mkf}*'
        print("MKF set up: ",cmd)
        mkf_arr.append(mkf)
    stat = os.system(cmd)
    cwd = os.getcwd()
    logs.stop_logging()
    
    return mkf_arr
