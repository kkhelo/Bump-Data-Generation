"""
*** Bump Parametric Generator (BPG) *** 
    This generator build bump from 2 parameters : k & c.
    k and c are recommended to be within range (0.5 ~ 2.5) and (0.0 ~ 0.4) respectively.


"""

import numpy as np 
import gmsh, sys


class BPG():
    def __init__(self, name : str = 'bump') -> None:
        self.geoPath = f'{name}.geo'
        self.mshPath = f'{name}.msh'
        self.name = name
        
    def buildCoorArray(self, k : float = 1.3, c : float = 0.1, xGrid : int = 21, yGrid : int = 41) -> list:
        delta = np.pi/28
        pts, index = [], 0
        for x in np.linspace(0, 1.0, xGrid)*np.pi:
            temp_x = x**2*np.tan(delta)**2 + c
            for y in np.linspace(-1.0, 1.0, yGrid)*np.pi:
                temp = temp_x/(1/np.cos(np.arctan(y/k)))**2
                z = np.sqrt(temp) * np.sin(x) * np.sin((y+np.pi)/2)
                pts.append([x, y, z])
                index += 1  

        self.pts = pts
        self.xGrid, self.yGrid = xGrid, yGrid

    def buildGeometry(self, bumpMeshSize : float = 0.005, plateMeshSize : float = 0.01, domainMeshSize : float = 0.5) -> None:

        gmsh.initialize()
        gmsh.model.add(self.name)
        bumpEdgePtsRight, bumpEdgePtsLeft, edgePts = [], [], [[]]

        # build the bump from corrdinate array
        for pt in self.pts :
            if pt[1] == 1.0 :
                bumpEdgePtsRight.append(gmsh.model.occ.add_point(*pt, meshSize=bumpMeshSize))
                edgePts[-1].append(bumpEdgePtsRight[-1])
                edgePts.append([])
            elif pt[1] == -1.0 :
                bumpEdgePtsLeft.append(gmsh.model.occ.add_point(*pt, meshSize=bumpMeshSize))
                edgePts[-1].append(bumpEdgePtsLeft[-1])
            else:
                edgePts[-1].append(gmsh.model.occ.add_point(*pt, meshSize=bumpMeshSize))

        edgePts.pop()        
        spanWiseSLine, streamWiseLineRight, streamWiseLineLeft = [], [], []
        for i in range(self.xGrid):
            spanWiseSLine.append(gmsh.model.occ.add_spline(edgePts[i]))

        for i in range(self.xGrid-1):
            streamWiseLineRight.append(gmsh.model.occ.add_line(bumpEdgePtsRight[i], bumpEdgePtsRight[i+1]))
            streamWiseLineLeft.append(gmsh.model.occ.add_line(bumpEdgePtsLeft[i], bumpEdgePtsLeft[i+1]))


if __name__ =='__main__':
    a = BPG()

    