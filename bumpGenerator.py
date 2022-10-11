"""
*** Bump Parametric Generator (BPG) *** 
    This generator build bump from 2 parameters : k & c.
    k and c are recommended to be within range (0.5 ~ 2.5) and (0.0 ~ 0.4) respectively.

"""

import numpy as np 
import gmsh, sys, os, time

class BPG():
    def __init__(self, name : str = 'bump', numThreads : int = 1, saveDir : str = './') -> None:
        gmsh.initialize(sys.argv)
        gmsh.model.add(name)
        # mesh file path 
        self.savePath = os.path.join(saveDir, name + '.msh')

        gmsh.option.setNumber('General.NumThreads', numThreads)
        gmsh.option.setNumber('General.Terminal', 1)
        # Set 3D alrorithm to HXT will produce error.
        gmsh.option.setNumber('Mesh.Algorithm3D', 1)
        gmsh.option.setNumber('Mesh.Algorithm', 8)
        gmsh.option.setNumber('Mesh.MshFileVersion', 2)
        
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

    def buildGeometry(self, bumpMeshSize : float = 0.01, plateMeshSize : float = 0.05, domainMeshSize : float = 0.5) -> None:
        
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
            temp = gmsh.model.geo.addCurveLoop([spanWiseSpline[i], streamWiseLineRight[i], spanWiseSpline[i+1], streamWiseLineLeft[i]], reorient=True)
            bumpSurface.append(gmsh.model.geo.addSurfaceFilling([temp]))

        # build plate points
        platePts = []
        for x in [-5, 3]:
            for y in [-3, 3]:
                platePts.append(gmsh.model.geo.addPoint(x, y, 0.00, meshSize=plateMeshSize))

        # swap order for convinience
        platePts[2], platePts[3] = platePts[3], platePts[2]

        # build plate line 
        plateLine = []
        for i in range(4):
            plateLine.append(gmsh.model.geo.addLine(platePts[i], platePts[(i+1)%4])) 

        plateLine.append(gmsh.model.geo.addLine(platePts[0], bumpPts[0][0]))
        plateLine.append(gmsh.model.geo.addLine(platePts[1], bumpPts[0][-1]))
        plateLine.append(gmsh.model.geo.addLine(platePts[2], bumpPts[-1][-1]))
        plateLine.append(gmsh.model.geo.addLine(platePts[3], bumpPts[-1][0]))

        # build plate surface
        plateSurface = []
        for i, bumpLine in zip(range(4), [spanWiseSpline[0], streamWiseLineRight, spanWiseSpline[-1], streamWiseLineLeft]):
            if type(bumpLine) is list : 
                temp = [plateLine[i], plateLine[(i+1)%4+4], *bumpLine, plateLine[i+4]]
            else:
                temp = [plateLine[i], plateLine[(i+1)%4+4], bumpLine, plateLine[i+4]]
            plateSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop(temp, reorient=True)]))

        # build domain points
        domainPtsBottom = []
        domainPtsUpper = []
        for x in [-15, 10]:
            for y in [-10, 10]:
                domainPtsBottom.append(gmsh.model.geo.addPoint(x, y, 0, meshSize=domainMeshSize))
                domainPtsUpper.append(gmsh.model.geo.addPoint(x, y, 10, meshSize=domainMeshSize))

        # swap order for convinience
        domainPtsBottom[2], domainPtsBottom[3] = domainPtsBottom[3], domainPtsBottom[2]
        domainPtsUpper[2], domainPtsUpper[3] = domainPtsUpper[3], domainPtsUpper[2]

        # build domain line 
        domainLineBottom = []
        domainLineTop = []
        for i in range(4):
            domainLineBottom.append(gmsh.model.geo.addLine(domainPtsBottom[i], domainPtsBottom[(i+1)%4]))
            domainLineTop.append(gmsh.model.geo.addLine(domainPtsUpper[i], domainPtsUpper[(i+1)%4]))

        for i in range(4):
            domainLineBottom.append(gmsh.model.geo.addLine(domainPtsBottom[i], platePts[i]))
            domainLineTop.append(gmsh.model.geo.addLine(domainPtsUpper[i], domainPtsBottom[i]))

        # build domain surface
        domainSurface = [[]]

        # bottom
        for i in range(4):
            temp = gmsh.model.geo.addCurveLoop([domainLineBottom[i], domainLineBottom[(i+1)%4+4], plateLine[i], domainLineBottom[i+4]], reorient=True)
            domainSurface[0].append(gmsh.model.geo.addPlaneSurface([temp]))
        
        # side
        for i in range(4):
            temp = gmsh.model.geo.addCurveLoop([domainLineBottom[i], domainLineTop[i+4], domainLineTop[i], domainLineTop[(i+1)%4+4]], reorient=True)
            domainSurface.append(gmsh.model.geo.addPlaneSurface([temp]))
        
        # top
        # domainSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([-domainLineTop[i] for i in range(3,-1,-1)], reorient=True)]))
        domainSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([-domainLineTop[i] for i in range(3,-1,-1)])]))

        self.domainSurface = domainSurface
        self.plateSurface = plateSurface
        self.bumpSurface = bumpSurface

        gmsh.model.geo.synchronize()

    def buildBlAndVolume(self, numLayers : int = 30, ratio : float = 1.2, firstHeight : float = 1e-4) -> None:
        
        # build boundary height array
        heights =[firstHeight]
        for i in range(1, numLayers):
            heights.append(heights[-1] + heights[0]*ratio**i)

        # build tag list for extrudeBoundaryLayer function
        tags = []
        for tag in self.plateSurface+self.bumpSurface:
            tags.append((2, -tag))

        # extrude boundary layer
        extbl = gmsh.model.geo.extrudeBoundaryLayer(tags, numElements=[1]*numLayers, heights=heights, recombine=True)

        # build bl top surface list, volume list and side surface list
        blSurfaceTop, blSurfaceSide, blVolume = [], [], []
        for i in range(1, len(extbl)):
            if extbl[i][0] == 3:
                blSurfaceTop.append(-extbl[i-1][1])
                blVolume.append(extbl[i][1])   
                if len(blSurfaceSide) < 4 :
                    blSurfaceSide.append(-extbl[i+2][1]) 

        # build volume
        temp = [*self.domainSurface[0][:2], *blSurfaceSide[:2], *blSurfaceTop, *blSurfaceSide[2:], *self.domainSurface[0][2:], *self.domainSurface[1:]]
        temp = gmsh.model.geo.addSurfaceLoop(temp)
        volume = blVolume + [gmsh.model.geo.addVolume([temp])]

        gmsh.model.geo.synchronize()

        gmsh.model.addPhysicalGroup(2, self.domainSurface[0], name='bottom')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[1]], name='inlet')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[2]], name='right')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[3]], name='outlet')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[4]], name='left')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[5]], name='top')
        gmsh.model.addPhysicalGroup(2, self.plateSurface, name='plate')
        gmsh.model.addPhysicalGroup(2, self.bumpSurface, name='bump')
        gmsh.model.addPhysicalGroup(3, volume, name='internal')

    def mesh(self, numRefine : int = 1):
        gmsh.model.mesh.generate(3)
        for i in range(numRefine):
            gmsh.model.mesh.refine()
        # gmsh.model.mesh.optimize()
        gmsh.write(self.savePath)
        if '-nopopup' not in sys.argv:
            gmsh.fltk.run()
        gmsh.finalize()


if __name__ =='__main__':
    startTime = time.time()
    a = BPG(numThreads=30)
    a.buildCoorArray(xGrid=41, yGrid=81)
    a.buildGeometry(bumpMeshSize=0.032, plateMeshSize=0.06, domainMeshSize=1.1)
    a.buildBlAndVolume(numLayers=10, firstHeight=0.0003, ratio=1.2)
    a.mesh()
    duration = (time.time() - startTime)/60
    print(f'Duration : {duration:.2f} mins')
