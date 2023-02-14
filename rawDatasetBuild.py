import random, os, sys,time

sys.path.append('helper')

from helper.dataBuilder import RDB

d = sys.argv[1]
samples = sys.argv[2]

os.system(f'cp -r hisaTemplate d{d}')

first = time.time()

for i in range(int(samples)):
    start = time.time()
    k = random.choice([50, 75, 100])
    c = random.choice([10, 30, 50])
    Mach = round(random.random()*1.5+1, 3)
    print(f'Case {i} start : \n\tGeometry : k{k}_c{c}_d{d} \n\tMach number: {Mach}')
    try :
        builder = RDB(geoName=f'k{k}_c{c}_d{d}', Mach=Mach, caseRoot=f'd{d}')
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