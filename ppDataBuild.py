"""

name : ppDataBuild.py
usage : build post processed dataset with specified raw data folder
flags : 
    * -n : number of processors, default is 1.
    * -o : override, default is False.
    * --rawpath : path to raw daraset, default is data/rawData.
    * --targetpath : path to post processed dataset, where the file will save to. Default is dada/demo.
    * --demo : activated demo mode. Demo mode creates figure from data but train mode doesn't. Default is train.
    * --geometry : specified geometry, this build only do 1 geometry not every in raw dataset.
author : Bo-Yuan You
Date : 2023-01-20

"""

import time, os, sys, getopt
import multiprocessing as mp
sys.path.append('helper')
from helper.dataBuilder import PPDB

cwd = os.getcwd()

def task(geoName, override = False, mode = 'train', targetPath='data/demo', rawDataRoot='data/rawData'):
    start = last = time.time()

    id = os.getpid()
    os.chdir(cwd)
    os.system(f'cp -r hisaPost ID{id}')

    temp = PPDB(geoName=geoName, caseRoot = f'ID{id}', targetPath=targetPath, rawDataRoot=rawDataRoot)
    temp.copyInclude()
    temp.linkMesh()

    print(geoName, temp.cases)

    for case in temp.cases:
        # case = '2.56'
        temp.linkTimeHistory(case)
        try :
            # temp.post(mode='train')
            temp.post(override=override, mode=mode, res=256)
            print(f'Case {geoName} @ {case} Mach end. Elapsed time {time.time() - last} seconds')
        except :
            print(f'Case {geoName} @ {case} Mach failed')

        temp.cleanUpTimeHistory()
        last = time.time()
        break

    temp.unLinkMesh()
    print(f'All cases in {geoName} completed. Total time elapsed {time.time() - start} seconds')
    os.chdir(cwd)
    os.system(f'rm -r ID{id}')

def main():
    targetPath, rawDataRoot = sys.argv[1], sys.argv[2]
    opts, args = getopt.getopt(sys.argv[1:], 'n:o', ['rawpath=', 'targetpath=', 'demo', 'geometry='])
    opts = dict(opts)

    rawDataRoot = opts['--rawpath'] if '--rawpath' in opts.keys() else 'data/rawData'
    targetPath = opts['--targetpath'] if '--targetpath' in opts.keys() else 'data/demo'
    override = True if '-o' in opts.keys() else False
    mode = 'demo' if '--demo' in opts.keys() else 'train'

    # If geometry is specified, do only one geometry
    if '--geometry' in opts.keys():
        geoName = opts['--geometry']
        task(geoName=geoName, override=override, mode=mode, targetPath=targetPath, rawDataRoot=rawDataRoot)
        return 

    numProcessors = int(opts['-n']) if '-n' in opts.keys() else 1
    

    if numProcessors == 1:
        for k in [50, 75, 100]:
            for c in [10, 30, 50]:
                for d in [14, 21, 28]:
                    geoName = f'k{k}_c{c}_d{d}'
                    task(geoName=geoName, override=override, mode=mode, targetPath=targetPath, rawDataRoot=rawDataRoot)
    else :
        pool = mp.Pool(numProcessors)
        for k in [50, 75, 100]:
            for c in [10, 30, 50]:
                for d in [14, 21, 28]:
                    geoName = f'k{k}_c{c}_d{d}'
                    pool.apply_async(task, args=(geoName, override, mode, targetPath, rawDataRoot))

        pool.close()
        pool.join()


if __name__ == '__main__':
    main()