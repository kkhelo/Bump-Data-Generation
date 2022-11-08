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
        gmsh.option.setNumber('General.ExpertMode', 1)
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

    def buildGeometry(self, bumpMeshSize : float = 0.01, plateMeshSize : float = 0.05, domainMeshSize : float = 0.5, scaleFactor : float = 1.0) -> None:
        
        bumpEdgePtsRight, bumpEdgePtsLeft, bumpPts = [], [], [[]]
        self.bumpMeshSize, self.plateMeshSize, self.domainMeshSize = bumpMeshSize, plateMeshSize, domainMeshSize

        # build bump points from corrdinates array
        for pt in self.pts :
            pt = list(np.array(pt)*scaleFactor)
            if pt[1] == 1.0*scaleFactor :
                bumpEdgePtsRight.append(gmsh.model.geo.addPoint(*pt, meshSize=bumpMeshSize))
                bumpPts[-1].append(bumpEdgePtsRight[-1])
                bumpPts.append([])
            elif pt[1] == -1.0*scaleFactor :
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
        self.yPlateSpan = [-2*scaleFactor, 2*scaleFactor]
        self.xPlateSpan = [-3*scaleFactor, 2*scaleFactor]
        for x in self.xPlateSpan:
            for y in self.yPlateSpan:
                platePts.append(gmsh.model.geo.addPoint(x, y, 0.00, meshSize=plateMeshSize))

        # swap order for convinience
        platePts[2], platePts[3] = platePts[3], platePts[2]
        self.platePts = platePts

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
        xDomainSpan = [-15*scaleFactor, 10*scaleFactor]
        yDomainSpan = [-10*scaleFactor, 10*scaleFactor]
        zTop = 10*scaleFactor
        for x in xDomainSpan:
            for y in yDomainSpan:
                domainPtsBottom.append(gmsh.model.geo.addPoint(x, y, 0, meshSize=domainMeshSize))
                domainPtsUpper.append(gmsh.model.geo.addPoint(x, y, zTop, meshSize=domainMeshSize))

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
        self.plateLine = plateLine[:4]

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
        # extbl = gmsh.model.geo.extrudeBoundaryLayer(tags, numElements=[1]*numLayers, heights=heights, recombine=True)
        extbl = gmsh.model.geo.extrudeBoundaryLayer(tags, numElements=[1]*numLayers, heights=heights)

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

        # mesh field distance from front and back plate line
        ySpan = self.yPlateSpan[-1] - self.yPlateSpan[0]
        gmsh.model.mesh.field.add('Distance', 1)
        gmsh.model.mesh.field.setNumbers(1, "CurvesList", [self.plateLine[0], self.plateLine[2]])
        gmsh.model.mesh.field.setNumber(1, 'Sampling', int(ySpan/self.bumpMeshSize)*4+1)

        # mesh field distance from right and left plate line
        xSpan = self.xPlateSpan[-1] - self.xPlateSpan[0]
        gmsh.model.mesh.field.add('Distance', 2)
        gmsh.model.mesh.field.setNumbers(2, "CurvesList", [self.plateLine[1], self.plateLine[3]])
        gmsh.model.mesh.field.setNumber(2, 'Sampling', int(xSpan/self.bumpMeshSize)*4+1)

        # mesh field distance from 4 plate points
        gmsh.model.mesh.field.add('Distance', 3)
        gmsh.model.mesh.field.setNumbers(3, "PointsList", self.platePts)

        # mesh control from distance field
        for i in range(4, 7):
            gmsh.model.mesh.field.add('Threshold', i)
            gmsh.model.mesh.field.setNumber(i, 'InField', i-3)
            gmsh.model.mesh.field.setNumber(i, "SizeMin", self.bumpMeshSize*0.1)
            gmsh.model.mesh.field.setNumber(i, "SizeMax", self.plateMeshSize)
            gmsh.model.mesh.field.setNumber(i, "DistMin", self.bumpMeshSize//4)
            gmsh.model.mesh.field.setNumber(i, "DistMax", self.bumpMeshSize*2)
            gmsh.model.mesh.field.setNumber(i, "StopAtDistMax", 1)

        # set background mesh
        gmsh.model.mesh.field.add("Min", 7)
        gmsh.model.mesh.field.setNumbers(7, "FieldsList", [4, 5, 6])
        gmsh.model.mesh.field.setAsBackgroundMesh(7)

        gmsh.model.addPhysicalGroup(2, self.domainSurface[0], name='bottom')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[1]], name='inlet')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[2]], name='right')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[3]], name='outlet')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[4]], name='left')
        gmsh.model.addPhysicalGroup(2, [self.domainSurface[5]], name='top')
        gmsh.model.addPhysicalGroup(2, self.plateSurface, name='plate')
        gmsh.model.addPhysicalGroup(2, self.bumpSurface, name='bump')
        gmsh.model.addPhysicalGroup(3, volume, name='internal')

        # free memory
        del self.domainSurface, self.domainMeshSize
        del self.plateSurface, self.plateLine, self.platePts, self.plateMeshSize, self.xPlateSpan, self.yPlateSpan
        del self.bumpSurface, self.bumpMeshSize

    def mesh(self, numRefine : int = 1):

        gmsh.option.setNumber("Mesh.Algorithm", 6)
        gmsh.option.setNumber('Mesh.Algorithm3D', 10)
        
        gmsh.model.mesh.generate(3)

        gmsh.write(self.savePath)
        gmsh.write('bump.vtk')
        
        gmsh.finalize()

  
if __name__ =='__main__':
    startTime = time.time()
    a = BPG(numThreads=16)
    a.buildCoorArray(xGrid=41, yGrid=81)
    a.buildGeometry(bumpMeshSize=0.02, plateMeshSize=0.05, domainMeshSize=0.5, scaleFactor=0.5)
    a.buildBlAndVolume(numLayers=12, firstHeight=0.0001, ratio=1.45)
    a.mesh()
    # gmsh.fltk.run()
    duration = (time.time() - startTime)/60
    print(f'Duration : {duration:.2f} mins')
