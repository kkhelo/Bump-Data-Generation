"""

name : databaseFieldMatrixGenerator.py
usage : Construct numpy array from openfoam postprocessed data
author : Bo-Yuan You
Date : 2023-01-11

"""


import os, glob, math
import numpy as np
import matplotlib.pyplot as plt


class DFMG():
    """
    databaseFieldMatrixGenerator (DFMG)

    Generator class construct 2 basic array with 1 additional array
        *** Basic
            * AIP (neighbor included)
            * surface (pressure and height)
        *** Additional 
            * xSlice and ySlice
    """

    MODE = ['TRAIN', 'TEST', 'DEMO']

    def __init__(self, srcPath : str, targetPath : str = './data/trainingData/', res : int = 256, mode : str = 'DEMO') -> None:
        self.__surfacePath = os.path.join(srcPath, 'postProcessing/boundaryCloud/*/surface_p.xy')
        self.__AIPPath = os.path.join(srcPath, 'postProcessing/internalCloud/*/AIP*.xy')
        self.__targetPath = targetPath
        self.__mode = mode.upper()
        if self.__mode not in self.MODE: 
            raise ValueError(F'Invalid Mode : {mode}, Available Options are (TRAIN, TEST, DEMO)')
        if not os.path.exists(self.__targetPath) : os.makedirs(self.__targetPath)
        self.resolution = res
        

    def constructSurfacePressureArray(self):
        """
        Read surface_p.xy in srcPath, and construct numpy array from it. 
        
        * Raise IOError if find zeor or multiple surface_p.xy file
        * Raise ValueError if number of data points is not equal to square of res
        """

        self.__surfacePath = glob.glob(self.__surfacePath)

        # Check if surfacePath exist 
        if len(self.__surfacePath) != 1 :
            raise IOError(f'There are {len(self.__surfacePath)} surface_p.xy in srcPath, should be 1.')
        
        self.__surfacePath = self.__surfacePath[0]
        pressureData = np.loadtxt(self.__surfacePath)

        # Check number of data points 
        nPts = pressureData.shape[0]
        if math.sqrt(nPts) - self.resolution != 0:
            raise ValueError(f'Number of data points is not math with resolution, nPts : {nPts}')

        heightsArray, pressureArray = pressureData[:,2], pressureData[:,3]
        heightsArray = np.resize(heightsArray, (self.resolution, self.resolution))
        pressureArray = np.resize(pressureArray, (self.resolution, self.resolution))

        np.savez_compressed(os.path.join(self.__targetPath, 'bumpSurfaceData'), heights = heightsArray, pressure = pressureArray)

        if self.__mode == 'DEMO': 
            plt.figure(figsize=(8,6))

            plt.tight_layout()
            plt.axis('off')
            plt.contourf(heightsArray, levels = 200, cmap='Greys')
            plt.colorbar()
            plt.savefig(os.path.join(self.__targetPath, 'surfaceHeight'))
            plt.close()

            plt.figure(figsize=(8,6))

            plt.tight_layout()
            plt.axis('off')
            plt.contourf(pressureArray, levels = 200, cmap='jet')
            plt.colorbar()
            plt.savefig(os.path.join(self.__targetPath, 'surfacePressure'))
            plt.close()
       
    def constructAIPFieldArray(self, fieldName : list = ['p', 'p0', 'rho', 'Ux', 'Uy', 'Uz']):
        """
        Read AIP_p_po_U.xy and its neighbors in srcPath, and construct numpy array from it. 
        File will be save in $srcPath/AIPData.npz will following keys

        * AIPData : 4-D array with size (numberOfNeighbors, numberOfFields, resolution, resolution)
        * geoMask : 3-D array with size (numberOfNeighbors, resolution, resolution)
        * AIPTags : 1-D array specified AIP tags, ex : ['AIP1', 'AIP', 'AIPM1']

        """

        self.__AIPPath = sorted(glob.glob(self.__AIPPath))
        neighbors = len(self.__AIPPath)
        AIPData = np.zeros((neighbors, len(fieldName), self.resolution, self.resolution))
        geoMask = np.zeros((neighbors, self.resolution, self.resolution))
        AIPTags = []
        
        for indexNeighbor, path in zip(range(neighbors), self.__AIPPath) :
            temp = np.zeros((len(fieldName), self.resolution, self.resolution))
            foamData = np.loadtxt(path)
            # yList = np.linspace(foamData[0,1], foamData[-1,1], self.resolution)
            zList = np.linspace(foamData[0,2], foamData[-1,2], self.resolution)           

            ptrFoamData = 0
            
            for i in range(self.resolution):
                for j in range(self.resolution):
                    if abs(foamData[ptrFoamData, 2]-zList[j]) <= 0.0001 :
                        temp[:,i,j] = foamData[ptrFoamData, 3:]
                        ptrFoamData += 1
                    else:
                        temp[:,i,j] = 0
                        geoMask[indexNeighbor,i,j] = 1

            AIPTags.append(path.split('/')[-1].split('_')[0])
            if self.__mode == 'DEMO' and AIPTags[-1] == 'AIP':
                # AIP flow field images
                for i in range(len(fieldName)):
                    plt.figure(figsize=(8,4))

                    plt.tight_layout()
                    plt.axis('off')
                    plt.contourf(temp[i].transpose(), levels = 200, cmap='jet')
                    plt.colorbar()
                    plt.savefig(os.path.join(self.__targetPath, f'AIP_{fieldName[i]}'))
                    plt.close()

                # AIP Mask images
                plt.figure(figsize=(8,4))
                plt.tight_layout()
                plt.axis('off')
                plt.contourf(geoMask[indexNeighbor].transpose(), levels = 200, cmap='Greys')
                plt.colorbar()
                plt.savefig(os.path.join(self.__targetPath, f'geoMask'))
                plt.close()

                # Total pressure recovery images
                TPR = temp[1]/np.max(temp[1])
                plt.figure(figsize=(8,4))
                plt.tight_layout()
                plt.axis('off')
                plt.contourf(TPR.transpose(), levels = 200, cmap='jet')
                plt.colorbar()
                plt.savefig(os.path.join(self.__targetPath, f'TPR'))
                plt.close()

            AIPData[indexNeighbor] = temp

        np.savez_compressed(os.path.join(self.__targetPath, 'AIPData'), AIPData = AIPData, geoMask=geoMask, AIPTags=AIPTags)

        
if __name__ == '__main__':
    srcPath = 'ID25065'
    targetPath = 'data/trainingData/k50_c10_d14/2.201/313'
    G = DFMG(srcPath=srcPath, targetPath=targetPath)
    G.constructAIPFieldArray()
    # G.constructSurfacePressureArray()

    
