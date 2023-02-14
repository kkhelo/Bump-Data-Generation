"""

name : dataBuilder.py
usage : Build raw data in following steps : 
        1. Link mesh file to case root folder
        2. Modified boundary condition (Mach number)
        3. Run simulation
        4. Create total pressure field 
        5. Move data file to target folder
author : Bo-Yuan You
Date : 2023-01-11

"""

import os
from bcMailMan import bcMailMan
from databaseFieldMatrixGenerator import DFMG

class RDB():
    """ 
    rawDataBuilder (RDB)

    Generator class build cfd raw data for given geometry parameters set and flow condition
    """

    # polyMesh files
    files = ['boundary', 'cellZones', 'faces', 'faceZones', 'neighbour', 'owner', 'points', 'pointZones']

    def __init__(self, geoName : str, Mach : float = 1.6, caseRoot : str = 'hisa', targetPath : str = 'data/rawData', failedCasePath : str = 'data/failedCase') -> None:

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
        status = os.system('mpirun -n 15 hisa -parallel > log.simulation')
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


class PPDB():
    """ 
    postProcessingDataBuilder (PPDB)

    Generator class build cfd raw data for given geometry parameters set and flow condition
    """

    # polyMesh files
    files = ['boundary', 'cellZones', 'faces', 'faceZones', 'neighbour', 'owner', 'points', 'pointZones']
    flowProperties = ['alphat', 'k', 'nut', 'omega', 'p', 'p0', 'pseudoCoField', 'rho', 'T', 'U', 'uniform/pseudoCoNum', 'uniform/pseudotimeState', 'uniform/time']

    def __init__(self, geoName: str, caseRoot: str = 'hisaPost', rawDataRoot : str = 'data/demoRawData', targetPath: str = 'data/demoData', failedPPCase : str = 'data/failedPPCase') -> None:
        self.__postProcessDataRoot = os.path.join(targetPath, geoName)
        self.__rawDataRoot = os.path.join(rawDataRoot, geoName)
        self.__meshPath = f'./preprocessing/{geoName}/mesh/polyMesh/'
        self.__caseRoot = caseRoot
        self.__failedPPCase = failedPPCase
        self.geoName = geoName
        os.makedirs(self.__postProcessDataRoot, exist_ok=True) 
        self.cases = os.listdir(self.__rawDataRoot)

    # Private
    def __checkTimeHistory(self, case) -> str :
        """
            Return time history from given case
            Raise error if time history doesn't exist
        """ 

        files = os.listdir(os.path.join(self.__rawDataRoot, case))
        if len(files) > 2:
            raise FileExistsError(f'More than 2 files or folder found in {os.path.join(self.__rawDataRoot, case)}')
        for file in files:
            if file.isdigit():
                return file
        
        raise FileExistsError(f'Unable to locate time history in {os.path.join(self.__rawDataRoot, case)}')

    def __failedCaseHandler(self, step : str, postProcessDataPath):
        os.removedirs(f'../{postProcessDataPath}')
        dst = os.path.join(f'../{self.__failedPPCase}', self.geoName, self.case, self.timeHistory)
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

    def linkTimeHistory(self, case):
        # Check if case exists
        if not os.path.exists(os.path.join(self.__rawDataRoot, case)) : 
            raise FileExistsError(f'Case {self.geoName} @ {case} Mach is not exist in {self.__rawDataRoot}!')
        
        self.timeHistory = self.__checkTimeHistory(case)

        if os.path.exists(os.path.join(self.__caseRoot, self.timeHistory, self.flowProperties[0])):
            self.cleanUpTimeHistory()
    
        rawDataRoot = os.path.join(self.__rawDataRoot, case, self.timeHistory)
        caseTempTimePath = os.path.join(self.__caseRoot, self.timeHistory)
        os.mkdir(caseTempTimePath)
        os.mkdir(os.path.join(caseTempTimePath, 'uniform'))
        
        for flowProperty in self.flowProperties:
            src = os.path.abspath(os.path.join(rawDataRoot, flowProperty))
            dst = os.path.abspath(os.path.join(caseTempTimePath, flowProperty))
            os.symlink(src, dst)
        
        self.case = case
    
    def cleanUpTimeHistory(self):
        for timeHistory in os.listdir(os.path.join(self.__caseRoot)):
            if timeHistory.isdigit() and int(timeHistory):
                path = os.path.join(self.__caseRoot, timeHistory)
                os.system(f'rm -r {path}')
        
        # Remove postProcessing folder
        temp = os.path.join(self.__caseRoot, 'postProcessing')
        os.system(f'rm -rf {temp}')

        # Delete timeHistory attribute
        if hasattr(self, 'timeHistory') : del self.timeHistory

    def copyInclude(self):
        dst = os.path.join(self.__caseRoot, 'system/include')
        if os.path.exists(dst):
            os.system(f'rm -r {dst}')

        src = os.path.join('preprocessing', self.geoName, 'system/include')
        os.system(f'cp -r {src} {dst}')

    def post(self, override : bool = False, mode='demo'):
        postProcessDataPath = os.path.join(self.__postProcessDataRoot, self.case, self.timeHistory)
        
        # Check if post process data exists in database 
        # Override old data if flag is on
        if os.path.exists(postProcessDataPath):
            if override :
                os.remove(postProcessDataPath)
            else : 
                raise FileExistsError(f'Case {self.geoName} @ {self.case} Mach is already exist in database!')

        os.makedirs(postProcessDataPath)

        os.chdir(self.__caseRoot)
        status = os.system('postProcess -latestTime -func boundaryCloud > log.boundaryCloud')
        if status != 0 : 
            self.__failedCaseHandler('boundaryCloud', postProcessDataPath)
        os.remove('log.boundaryCloud')

        status = os.system('postProcess -latestTime -func internalCloud > log.internalCloud')
        if status != 0 : 
            self.__failedCaseHandler('internalCloud', postProcessDataPath)
        os.remove('log.internalCloud')
        os.chdir('..')

        generator = DFMG(srcPath=self.__caseRoot, targetPath=postProcessDataPath, mode=mode)
        generator.constructAIPFieldArray()
        generator.constructSurfacePressureArray()
        


if __name__ == '__main__':

    # temp = RDB(geoName='k75_c10_d14', Mach=2.8, caseRoot='./12589', targetPath='data/rawData')

    # temp.linkMesh()
    # temp.sim()
    # temp.post()
    # temp.unLinkMesh()

    import time

    start = last = time.time()
    temp = PPDB(geoName='k50_c10_d14')
    temp.copyInclude()
    temp.linkMesh()
    
    for case in temp.cases[1:]:
        print(f'Case {case} Mach begin')
        temp.linkTimeHistory(case)
        temp.post()
        temp.cleanUpTimeHistory()
        print(f'Case {case} Mach end')
        now = time.time()
        print(f'Elapsed time {now - last} seconds')
        last = now
    temp.unLinkMesh()
    print(f'All cases completed')
    print(f'Elapsed time {time.time() - start} seconds')

    # generator = DFMG(srcPath='hisaPost', targetPath='data/demoData/k50_c10_d14/2.441/312', mode='demo')
    # generator.constructAIPFieldArray()
    # generator.constructSurfacePressureArray()