########################################
#
# name : pointsCloundGenerator.py
# usage : To generate internal clound 'points set' for gethering flow field value at specific locations
# author : Bo-Yuan You
# Date : 2022-11-28
#
########################################


import numpy as np
import matplotlib.pyplot as plt
import os


def ySlice(yCoor : float = 0.0, xBound = [-0.25, 0.75], zBound = [0, 0.5], res : float = 256, fileDir = '', pointName = None):
        fileDir = os.path.join(fileDir, pointName) if pointName else os.path.join(fileDir, f'y={yCoor}')
        dx, dz = (xBound[-1]-xBound[0])/res, (zBound[-1]-zBound[0])/res
        xList = np.linspace(xBound[0]+dx, xBound[-1]-dx, res)
        zList = np.linspace(zBound[0]+dz, zBound[-1]-dz, res)
        with open(fileDir, 'w') as of:
            if pointName :
                of.write(pointName + '\n')
            else:
                of.write(f'pointsY{int(yCoor*100)}\n')
            of.write('(\n')
            for x in xList:
                for z in zList:
                    of.write(f'({x} {yCoor} {z})\n')
            of.write(');\n')

def xSlice(xCoor : any = [0.0], yBound = [-0.5, 0.5], zBound = [0, 0.5], res : float = 256, fileDir = '', pointName = None):
        if type(xCoor) is not list:
            try:
                xCoor = [xCoor]
            except:
                raise ValueError('Invalid xCoor data type. Expected list, float or int')
            
        fileDir = os.path.join(fileDir, pointName) if pointName else os.path.join(fileDir, f'x={xCoor[0]}')
        dx, dz = (yBound[-1]-yBound[0])/res, (zBound[-1]-zBound[0])/res
        yList = np.linspace(yBound[0]+dx, yBound[-1]-dx, res)
        zList = np.linspace(zBound[0]+dz, zBound[-1]-dz, res)
        with open(fileDir, 'w') as of:
            if pointName :
                of.write(pointName + '\n')
            else:
                of.write(f'pointsX{int(xCoor[0]*100)}\n')
            of.write('(\n')
            for x in xCoor:
                for y in yList:
                    for z in zList:
                        of.write(f'({x} {y} {z})\n')
            of.write(');\n')

class bumpProbesWriter():
    """
    Create probes point cloud file for given bump geometry parameters. 
    
    DEBUG flag sets to False will supress file clean up information
    """
    def __init__(self, k : float, c : float, d : int, xBound = [0, 1], yBound = [-1, 1], zBound = [0, 1], scaleFactor : float = 0.5, res : int = 256, rootDir : str = '', DEBUG : bool = True) -> None:
        self.__bumpName = f'k{int(k*100):d}_c{int(c*100):d}_d{d}'
        self.__res = res
        self.__DEBUG = DEBUG
        self.__rootDir = os.path.join(rootDir, self.__bumpName, 'system', 'include')
        if not os.path.exists(self.__rootDir):
            os.makedirs(self.__rootDir, exist_ok=True)
        # os.makedirs(os.path.join(rootDir, self.__bumpName, 'mesh'), exist_ok=True)

        # Construct bump surface corrdinates matrix
        delta = np.pi/d
        dx, dy = (xBound[-1]-xBound[0])/res, (yBound[-1]-yBound[0])/res
        __xList = np.linspace(xBound[0]+dx, xBound[-1]-dx, res)
        __yList = np.linspace(yBound[0]+dy, yBound[-1]-dy, res)
        self.__zSurfacePoints = np.zeros((res, res))
        for i, x in zip(range(res), __xList):
            x *= np.pi
            temp_x = x**2*np.tan(delta)**2 + c
            for j, y in zip(range(res), __yList):
                y *= np.pi 
                temp = temp_x/(1/np.cos(np.arctan(y/k)))**2
                self.__zSurfacePoints[i, j]  = np.sqrt(temp) * np.sin(x) * np.sin((y+np.pi)/2) * scaleFactor

        self.__xList = __xList * scaleFactor
        self.__yList = __yList * scaleFactor
        self.__scaleFactor = scaleFactor
        self.__zBound = zBound

    def writeSurface(self):
        # fileDir = os.path.join(fileRootDir, self.__bumpName + '_surface')
        fileDir = os.path.join(self.__rootDir, 'surface')
        with open(fileDir, 'w') as of:
            of.write('bump\n')
            of.write('(\n')
            for i, x in zip(range(self.__res), self.__xList):
                for j, y in zip(range(self.__res), self.__yList):
                    of.write(f'({x} {y} {self.__zSurfacePoints[i, j]})\n')

            of.write(');\n')
    
    def AIP(self, neighbor : int = 1, neighborSpacing : float = 0.05):
        
        self.cleanAIPSlices()
        bumpApex = np.max(self.__zSurfacePoints)
        AIPLocation = self.__xList[np.where(self.__zSurfacePoints == bumpApex)[0][0]]
        
        xSlice(xCoor=AIPLocation, zBound=self.__zBound, res=self.__res, fileDir=self.__rootDir, pointName='AIP')
        for i in range(1, neighbor+1) :
            if (AIPLocation + i * neighborSpacing > self.__xList[-1]) or (AIPLocation - i * neighborSpacing < self.__xList[0]) : 
                return
            xSlice(xCoor=AIPLocation + i * neighborSpacing, zBound=self.__zBound, res=self.__res, fileDir=self.__rootDir, pointName=f'AIP{i}')
            xSlice(xCoor=AIPLocation - i * neighborSpacing, zBound=self.__zBound, res=self.__res, fileDir=self.__rootDir, pointName=f'AIPm{i}')

    def flowDirectionalSlice(self, nSlices : int = 5):
        """
        Create flowDirectional slices span bump length.
        Automatically clean up previous flowDirectional slices before create new
        """
        self.cleanFlowDirectionalSlices()
        xList = np.linspace(0, self.__scaleFactor*1, nSlices)
        os.system(f'rm -rf {self.__rootDir}/x*')
        for i, x in zip(range(1, nSlices+1), xList):
            xSlice(x, zBound=self.__zBound, res=self.__res, fileDir=self.__rootDir, pointName=f'x{i}')

    def cleanFlowDirectionalSlices(self):
        """
        Clean up flowDirectional slices in given root path
        """
        fileList = os.listdir(self.__rootDir)
        if 'x1' not in fileList :
            if self.__DEBUG : print(f'None of flowDirectional slice file found in {self.__rootDir}')
            return
        
        for file in fileList:
            if 'x' in file:
                os.remove(os.path.join(self.__rootDir, file))

        if self.__DEBUG :  print(f'Clean up flowDirecitonal slice files in {self.__rootDir}')    

    def cleanAIPSlices(self):
        """
        Clean up AIP slices in given root path
        """
        fileList = os.listdir(self.__rootDir)
        if 'AIP' not in fileList :
            if self.__DEBUG :  print(f'None of AIP slice file found in {self.__rootDir}')
            return
        
        for file in fileList:
            if 'AIP' in file:
                os.remove(os.path.join(self.__rootDir, file))

        if self.__DEBUG :  print(f'Clean up AIP slice files in {self.__rootDir}')   


if __name__ == '__main__' :
    
    ###############################################################
    # # Training geometry
    # for k in [0.5, 0.75, 1.0]:
    #     for c in [0.1, 0.3, 0.5]:
    #         for d in [14, 21, 28]:
    #             bumpName = f'k{int(k*100):d}_c{int(c*100):d}_d{d}'

    #             # G = bumpProbesWriter(k, c, d, rootDir='preprocessing', res=256)
    #             G = bumpProbesWriter(k, c, d, rootDir='preprocessing', res=256)
    #             G.writeSurface()
    #             G.AIP(neighbor=0, neighborSpacing=0.02)
    #             if not os.path.exists(f'preprocessing/{bumpName}/mesh'):
    #                 os.mkdir(f'preprocessing/{bumpName}/mesh')
    #             # G.flowDirectionalSlice(nSlices=5)
    #             # G.cleanFlowDirectionalSlices()
    #             # G.cleanAIPSlices()

    # Testing geometry
    # for k in [0.6, 0.8]:  
    #     for c in [0.2, 0.4]:
    #         for d in [20, 30]:
    #             bumpName = f'k{int(k*100):d}_c{int(c*100):d}_d{d}'

    #             # G = bumpProbesWriter(k, c, d, rootDir='preprocessing', res=256)
    #             G = bumpProbesWriter(k, c, d, rootDir='preprocessing', res=256)
    #             G.writeSurface()
    #             G.AIP(neighbor=0, neighborSpacing=0.02)
    #             if not os.path.exists(f'preprocessing/{bumpName}/mesh'):
    #                 os.mkdir(f'preprocessing/{bumpName}/mesh')
    #             # G.flowDirectionalSlice(nSlices=5)
    #             # G.cleanFlowDirectionalSlices()
    #             # G.cleanAIPSlices()
    
    ################################################################
    # import random

    # random_list = sorted([round(random.uniform(0.05, 0.45), 3) for _ in range(10)])
    
    # print(random_list)

    # xSlice(random_list, pointName='slice', fileDir='')

    ################################################################

    # demo geometry
    k, c, d = 0.5, 0.5, 14
    bumpName = f'k{int(k*100):d}_c{int(c*100):d}_d{d}'

    # G = bumpProbesWriter(k, c, d, rootDir='preprocessing', res=256)
    G = bumpProbesWriter(k, c, d, rootDir='demo', res=64)
    G.writeSurface()
    # G.AIP(neighbor=0, neighborSpacing=0.02)
    if not os.path.exists(f'preprocessing/{bumpName}/mesh'):
        os.mkdir(f'preprocessing/{bumpName}/mesh')
    # G.flowDirectionalSlice(nSlices=5)
    # G.cleanFlowDirectionalSlices()
    # G.cleanAIPSlices()