
import time, os, sys
sys.path.append('helper')
from helper.dataBuilder import PPDB

import multiprocessing as mp

numThread = 9

def task(geoName):
    start = last = time.time()

    id = os.getpid()
    os.system(f'cp -r hisaPost ID{id}')

    temp = PPDB(geoName=geoName, caseRoot = f'ID{id}')
    temp.copyInclude()
    temp.linkMesh()

    print(geoName, temp.cases)

    for case in temp.cases:
        temp.linkTimeHistory(case)
        try :
            temp.post(mode='train')
            print(f'Case {geoName} @ {case} Mach end. Elapsed time {time.time() - last} seconds')
        except :
            print(f'Case {geoName} @ {case} Mach failed')

        temp.cleanUpTimeHistory()
        last = time.time()

    temp.unLinkMesh()
    print(f'All cases in {geoName} completed. Total time elapsed {time.time() - start} seconds')
    os.system(f'rm -r ID{id}')

def main():
    pool = mp.Pool(numThread)

    for k in [50, 75, 100]:
        for c in [10, 30, 50]:
            for d in [14, 21, 28]:
                geoName = f'k{k}_c{c}_d{d}'
                pool.apply_async(task, args=(geoName,))

    pool.close()
    pool.join()


if __name__ == '__main__':
    main()