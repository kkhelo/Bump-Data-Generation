"""

name : bcMailMan.py
usage : To write freestream conditions by given Mach to specified openFoam case
author : Bo-Yuan You
Date : 2023-01-11

"""


import math, os

def bcMailMan(caseRootDir : str, Mach : float, T : float = 300.0, I : float = 0.001, mixingLength : float = 1e-5) -> None:
    fileDir = os.path.join(caseRootDir, '0.org/include/freestreamConditions')
    print(fileDir)

    # Sound speed
    a = math.sqrt(1.4*287*T)    
    # Freestream Velocity
    U = a*Mach                  
    # SST-KOmega turbulence K = 1.5*(UI)^2
    k = 1.5 * (U * I) ** 2
    # SST-KOmega turbulence omega = 0.09^(-0.25)*k^0.5/mixingLength
    omega = 0.09**(-0.25)*k**0.5/mixingLength

    os.system(f'foamDictionary hisa/0.org/include/freestreamConditions -entry Ux -set {U:.2f}')
    os.system(f'foamDictionary hisa/0.org/include/freestreamConditions -entry k -set {k:.3f}')
    os.system(f'foamDictionary hisa/0.org/include/freestreamConditions -entry omega -set {int(omega):d}')
    if T != 300 : os.system(f'foamDictionary hisa/0.org/include/freestreamConditions -entry T -set {T}')


if __name__ == '__main__' :
    bcMailMan(caseRootDir='hisa', Mach=1.6)