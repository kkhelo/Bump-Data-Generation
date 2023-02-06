import random, os, sys,time

sys.path.append('helper')

from helper.rawDataBuilder import RDB

d = sys.argv[1]
samples = sys.argv[2]

os.system(f'cp -r hisaTemplate d{d}')

first = time.time()

for i in samples:
    start = time.time()
    k = random.choice([50, 75, 100])
    c = random.choice([10, 30, 50])
    Mach = round(random.random()*1.5+1, 3)
    builder = RDB(geoName=f'k{k}_c{c}_d{d}', Mach=Mach, caseRoot=f'd{d}')
    builder.linkMesh()
    builder.sim()
    builder.post()
    builder.unLinkMesh()
    print(f'Case k{k}_c{c}_d{d} at {Mach} Mach done')
    print(f'Time elapsed for 1 case : {(time.time()-start)/60} mins')
    print(f'Total time elapsed  : {(time.time()-first)/60} mins')
        
