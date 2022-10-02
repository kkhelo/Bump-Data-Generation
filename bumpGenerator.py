"""
*** Bump Parametric Generator (BPG) *** 
    This generator build bump from 2 parameters : k & c.
    k and c are recommended to be within range (0.5 ~ 2.5) and (0.0 ~ 0.4) respectively.


"""

import numpy as np 
import gmsh, sys

from pyparsing import line


class BPG():
    def __init__(self, name : str = 'bump', numThreads : int = 1) -> None:
        self.geoPath = f'{name}.geo'
        self.mshPath = f'{name}.msh'
        self.name = name
        self.nt = numThreads
        
    def buildCoorArray(self, k : float = 1.3, c : float = 0.1, xGrid : int = 21, yGrid : int = 41) -> list:
        delta = np.pi/28
        pts, index = [], 0
        for x in np.linspace(0, 1.0, xGrid)*np.pi:
            temp_x = x**2*np.tan(delta)**2 + c
            for y in np.linspace(-1.0, 1.0, yGrid)*np.pi:
                temp = temp_x/(1/np.cos(np.arctan(y/k)))**2
                z = np.sqrt(temp) * np.sin(x) * np.sin((y+np.pi)/2)
                pts.append([x/np.pi, y/np.pi, z])
                index += 1  

        self.pts = pts
        self.xGrid, self.yGrid = xGrid, yGrid

    def buildGeometry(self, bumpMeshSize : float = 0.01, plateMeshSize : float = 0.05, domainMeshSize : float = 1) -> None:

        gmsh.initialize()
        gmsh.model.add(self.name)
        gmsh.option.setNumber('General.NumThreads', self.nt)
        gmsh.option.setNumber('Mesh.Algorithm3D', 10)
        gmsh.option.setNumber('General.ExpertMode', 1)
        
        bumpEdgePtsRight, bumpEdgePtsLeft, bumpPts = [], [], [[]]

        # build bump points from corrdinates array
        for pt in self.pts :
            if pt[1] == 1.0 :
                bumpEdgePtsRight.append(gmsh.model.geo.addPoint(*pt, meshSize=bumpMeshSize))
                bumpPts[-1].append(bumpEdgePtsRight[-1])
                bumpPts.append([])
            elif pt[1] == -1.0 :
                bumpEdgePtsLeft.append(gmsh.model.geo.addPoint(*pt, meshSize=bumpMeshSize))
                bumpPts[-1].append(bumpEdgePtsLeft[-1])
            else:
                bumpPts[-1].append(gmsh.model.geo.addPoint(*pt, meshSize=bumpMeshSize))
        bumpPts.pop()        

        # build bump surface 
        spanWiseSpline, streamWiseLineRight, streamWiseLineLeft = [], [], []
        for i in range(self.xGrid):
            spanWiseSpline.append(gmsh.model.geo.addSpline(bumpPts[i]))

        for i in range(self.xGrid-1):
            streamWiseLineRight.append(gmsh.model.geo.addLine(bumpEdgePtsRight[i], bumpEdgePtsRight[i+1]))
            streamWiseLineLeft.append(gmsh.model.geo.addLine(bumpEdgePtsLeft[i], bumpEdgePtsLeft[i+1]))

        # build bump surface 
        bumpSurface = []
        for i in range(self.xGrid-1):
            temp = gmsh.model.geo.addCurveLoop([spanWiseSpline[i], streamWiseLineRight[i], -spanWiseSpline[i+1], -streamWiseLineLeft[i]])
            bumpSurface.append(gmsh.model.geo.addSurfaceFilling([temp]))

        # build plate points
        platePts = []
        for x in [-5, 3]:
            for y in [-3, 3]:
                platePts.append(gmsh.model.geo.addPoint(x, y, 0.00, meshSize=plateMeshSize))

        # swap order and add first node for convinience
        platePts[2], platePts[3] = platePts[3], platePts[2]
        platePts.append(platePts[0])

        # build plate line 
        plateLine = []
        for i in range(4):
            plateLine.append(gmsh.model.geo.addLine(platePts[i], platePts[i+1])) 
        platePts.pop()

        plateLine.append(gmsh.model.geo.addLine(platePts[0], bumpPts[0][0]))
        plateLine.append(gmsh.model.geo.addLine(platePts[1], bumpPts[0][-1]))
        plateLine.append(gmsh.model.geo.addLine(platePts[2], bumpPts[-1][-1]))
        plateLine.append(gmsh.model.geo.addLine(platePts[3], bumpPts[-1][0]))

        # build plate surface
        plateSurface = []
        
        plateSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([plateLine[0], plateLine[5], -spanWiseSpline[0], -plateLine[4]])]))
        temp = [plateLine[1], plateLine[6]]
        for line in streamWiseLineRight[-1::-1]:
            temp.append(-line)
        temp.append(-plateLine[5])
        plateSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop(temp)]))
        plateSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([plateLine[2], plateLine[7], spanWiseSpline[-1], -plateLine[6]])]))
        plateSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([plateLine[3], plateLine[4], *streamWiseLineLeft, -plateLine[7]])]))

        gmsh.model.geo.synchronize()



if __name__ =='__main__':
    a = BPG(numThreads=20)
    a.buildCoorArray(xGrid=41, yGrid=81)
    a.buildGeometry()
    if '-nopopup' not in sys.argv:
        gmsh.fltk.run()
    gmsh.finalize()