"""

name : rawDatasetBuild.py
usage : build raw dataset with specified cone angle and number.
flags : 
    * -d : cone angle, must declare.
    * --samples : number of data to build, default is 10.
    * --targetpath : path to post processed dataset, where the file will save to. Default is data/rawData.
author : Bo-Yuan You
Date : 2023-01-15

"""


import random, os, sys, time, getopt

sys.path.append('helper')

from helper.dataBuilder import RDB

opts, args = getopt.getopt(sys.argv[1:], 'd:', ['samples=', 'targetpath='])
opts = dict(opts)
d = opts['-d']
samples = opts['--samples'] if '--samples' in opts.keys() else 10
targetPath = opts['--targetpath'] if '--targetpath' in opts.keys() else 'data/rawData'

os.system(f'cp -r hisaTemplate d{d}')

first = time.time()

for i in range(int(samples)):
    start = time.time()
    k = random.choice([50, 75, 100])
    c = random.choice([10, 30, 50])
    Mach = round(random.random()*1.5+1, 3)
    print(f'Case {i} start : \n\tGeometry : k{k}_c{c}_d{d} \n\tMach number: {Mach}')
    try :
        builder = RDB(geoName=f'k{k}_c{c}_d{d}', Mach=Mach, caseRoot=f'd{d}', targetPath=targetPath)
    except : 
        print(f'Case exist, terminating!')
        continue
    builder.linkMesh()
    builder.sim()
    builder.post()
    builder.unLinkMesh()
    print(f'Case {i} done')
    print(f'Time elapsed for 1 case : {(time.time()-start)/60} mins')
    print(f'Total time elapsed  : {(time.time()-first)/60} mins')
        
os.system(f'rm -rf d{d}')