"""

name : rawDataBuilder.py
usage : Build raw data in following steps : 
        1. Link mesh file to case root folder
        2. Modified boundary condition (Mach number)
        3. Run simulation
        4. Create total pressure field 
        5. Move data file to target folder
author : Bo-Yuan You
Date : 2023-01-11

"""

import numpy as np
import os, sys
from bcMailMan import bcMailMan

class RDB():
    """ 
    rawDataBuilder (RDB)

    Generator class build cfd raw data for given geometry parameters set and flow condition
    """

    # polyMesh files
    files = ['boundary', 'cellZones', 'faces', 'faceZones', 'neighbour', 'owner', 'points', 'pointZones']

    def __init__(self, geoName : str, Mach : float = 1.6, caseRoot : str = 'hisa', targetPath : str = 'data/rawData', failedCasePath : str = 'failedCase') -> None:

        self.__rawDataPath = os.path.join(targetPath, geoName, str(Mach))
        # Check if case is been done or not
        if os.path.exists(self.__rawDataPath) and os.listdir(self.__rawDataPath):
            raise FileExistsError(f'Case {geoName} @ {Mach} Mach is already exist in database!')
        os.makedirs(self.__rawDataPath, exist_ok=True)

        self.geoName = geoName
        self.Mach = Mach
        self.__meshPath = f'./preprocessing/{geoName}/mesh/polyMesh/'
        self.__failedCasePath = failedCasePath
        self.__caseRoot = caseRoot
        # flag of whether bc is set of not
        self.__bcFlag = False

    # Private
    def __findLatest(self):
        for path in os.listdir(self.__caseRoot):
            if path.isdigit() and int(path):
                self.latestTime = int(path)
                return

    def __failedCaseHandler(self, step : str):
        os.removedirs(f'../{self.__rawDataPath}')
        dst = os.path.join(f'../{self.__failedCasePath}', self.geoName, str(self.Mach))
        os.makedirs(dst)
        os.system(f'mv log.{step} {dst}')
        os.chdir('..')
        raise RuntimeError(f'Error occurs at {step} step!')

    # Public
    def linkMesh(self):
        if os.path.exists(os.path.abspath(os.path.join(self.__caseRoot, f'constant/polyMesh/{self.files[0]}'))):
            self.unLinkMesh()

        for file in self.files:
            # Relative path raise errors
            src = os.path.abspath(os.path.join(self.__meshPath, file))
            dst = os.path.abspath(os.path.join(self.__caseRoot, f'constant/polyMesh/{file}'))
            os.symlink(src, dst)

    def unLinkMesh(self):
        # Check if files is linked
        if os.path.exists(os.path.abspath(os.path.join(self.__caseRoot, f'constant/polyMesh/{self.files[0]}'))):
            # Delete links in order
            for file in self.files:
                os.unlink(os.path.abspath(os.path.join(self.__caseRoot, f'constant/polyMesh/{file}')))

    def setBC(self):
        if not self.__bcFlag :
            bcMailMan(self.__caseRoot, self.Mach)

    def sim(self):
        self.setBC()
        os.chdir(self.__caseRoot)
        
        # Copy 0
        os.system('rm -rf 0')
        os.system('cp -r 0.org 0')

        # Decompose
        status = os.system('decomposePar > log.decompose')
        if status != 0 : 
            self.__failedCaseHandler('decompose')
        os.remove('log.decompose')

        # Simulation
        status = os.system('mpirun -n 14 hisa -parallel > log.simulation')
        if status != 0 : 
            self.__failedCaseHandler('simulation')

        # Reconstruct
        status = os.system('reconstructPar > log.reconstruct')
        if status != 0 : 
            self.__failedCaseHandler('reconstruct')
        os.remove('log.reconstruct')

        # Clean up
        os.system('rm -r processor*')
        os.chdir('..')
        
    def post(self):
        # Rename total(p) in latest time history
        self.__findLatest()
        src = os.path.join(self.__caseRoot, str(self.latestTime), 'total(p)')
        if os.path.exists(src):
            os.rename(src, os.path.join(self.__caseRoot, str(self.latestTime), 'p0'))

        # Move data to target path
        src = os.path.join(self.__caseRoot, str(self.latestTime))
        dst = os.path.join(self.__rawDataPath)
        os.system(f'mv {src} {dst}')

        # Move log
        src = os.path.join(self.__caseRoot, 'log.simulation')
        dst = os.path.join(self.__rawDataPath, 'log.simulation')
        os.system(f'mv {src} {dst}')



if __name__ == '__main__':

    temp = RDB(geoName='k75_c10_d14', Mach=2.8, caseRoot='./12589', targetPath='data/rawData')

    # temp.linkMesh()
    # temp.sim()
    temp.post()
    # temp.unLinkMesh()