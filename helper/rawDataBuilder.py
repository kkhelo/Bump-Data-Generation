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

    def __init__(self, geoName : str, Mach : float = 1.6, caseRoot : str = 'hisa') -> None:
        self.geoName = geoName
        self.Mach = Mach
        self.__meshPath = f'./preprocessing/{geoName}/mesh/polyMesh/'
        self.__caseRoot = caseRoot
        # flag of whether bc is set of not
        self.__bcFlag = False

    # Private
    def __findLatest(self):
        for path in os.listdir(self.__caseRoot):
            if path.isdigit() and int(path):
                os.rename(os.path.join(self.__caseRoot, path, 'total(p)'), os.path.join(self.__caseRoot, path, 'p0'))
                self.latestTime = int(path)
                return

    # Public
    def linkMesh(self):
        for file in self.files:
            # Relative path raise errors
            src = os.path.abspath(os.path.join(self.__meshPath, file))
            dst = os.path.abspath(os.path.join(self.__caseRoot, f'constant/polyMesh/{file}'))
            os.symlink(src, dst)

    def unLinkMesh(self):
        for file in self.files:
            os.unlink(os.path.abspath(os.path.join(self.__caseRoot, f'constant/polyMesh/{file}')))

    def setBC(self):
        if not self.__bcFlag :
            bcMailMan(self.__caseRoot, self.Mach)

    def sim(self):
        self.setBC()
        os.chdir(self.__caseRoot)
        os.system('./runSim')

    def post(self):
        pass
if __name__ == '__main__':
    temp = RDB(geoName='k50_c10_d14', Mach=1.4, caseRoot='./12509')
    # temp.linkMesh()
    # temp.unLinkMesh()
    # temp.findLatest()