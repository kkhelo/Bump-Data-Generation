import gmsh, sys
import numpy as np

def bumpTriGen(bumpMeshSize : float = 0.01, plateMeshSize : float = 0.05, k : float = 1.3, c : float = 0.1, xGrid : int = 51, yGrid : int = 101, scaleFactor : float = 1.0) -> None:

        gmsh.initialize(sys.argv)
        gmsh.model.add('bump')

        gmsh.option.setNumber('General.NumThreads', 20)
        gmsh.option.setNumber('General.Terminal', 1)
        gmsh.option.setNumber('General.ExpertMode', 1)
        gmsh.option.setNumber('Mesh.MshFileVersion', 2)

        delta = np.pi/28
        pts, index = [], 0
        for x in np.linspace(0, 1.0, xGrid)*np.pi:
            temp_x = x**2*np.tan(delta)**2 + c
            for y in np.linspace(-1.0, 1.0, yGrid)*np.pi:
                temp = temp_x/(1/np.cos(np.arctan(y/k)))**2
                z = np.sqrt(temp) * np.sin(x) * np.sin((y+np.pi)/2)
                pts.append([x/np.pi, y/np.pi, z])
                index += 1  

        bumpEdgePtsRight, bumpEdgePtsLeft, bumpPts = [], [], [[]]

        # build bump points from corrdinates array
        for pt in pts :
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
        for i in range(xGrid):
            spanWiseSpline.append(gmsh.model.geo.addSpline(bumpPts[i]))

        for i in range(xGrid-1):
            streamWiseLineRight.append(gmsh.model.geo.addLine(bumpEdgePtsRight[i], bumpEdgePtsRight[i+1]))
            streamWiseLineLeft.append(gmsh.model.geo.addLine(bumpEdgePtsLeft[i], bumpEdgePtsLeft[i+1]))

        # build bump surface 
        bumpSurface = []
        for i in range(xGrid-1):
            temp = gmsh.model.geo.addCurveLoop([spanWiseSpline[i], streamWiseLineRight[i], spanWiseSpline[i+1], streamWiseLineLeft[i]], reorient=True)
            bumpSurface.append(gmsh.model.geo.addSurfaceFilling([temp]))

        temp = gmsh.model.geo.addCurveLoop([spanWiseSpline[0], *streamWiseLineRight, spanWiseSpline[-1], *streamWiseLineLeft], reorient=True)
        bumpBottomSurface = gmsh.model.geo.addPlaneSurface([temp])
        bumpSurface.append(bumpBottomSurface)

        # build plate points
        platePts = []
        for x in [-3, 2]:
            for y in [-2, 2]:
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
        for i, bumpLine in zip(range(4), [spanWiseSpline[0], streamWiseLineRight, spanWiseSpline[-1], streamWiseLineLeft]):
            if type(bumpLine) is list : 
                temp = [plateLine[i], plateLine[(i+1)%4+4], *bumpLine, plateLine[i+4]]
            else:
                temp = [plateLine[i], plateLine[(i+1)%4+4], bumpLine, plateLine[i+4]]
            bumpSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop(temp, reorient=True)]))

        gmsh.model.geo.synchronize()
        gmsh.model.addPhysicalGroup(2, bumpSurface, name='bump')

        gmsh.option.setNumber("Mesh.Algorithm", 5)
        
        gmsh.model.mesh.generate(2)

        name = sys.argv[1]
        gmsh.write(f'{name}.stl')
        # gmsh.write(f'{name}.vtk')
        
        gmsh.finalize()

def fakeBumpGen():
    gmsh.initialize(sys.argv)
    gmsh.model.add('fakeBump')

    gmsh.option.setNumber('General.Terminal', 1)
    gmsh.option.setNumber('General.ExpertMode', 1)

    bumpPts = []

    # build bump points from corrdinates array
    for x in [0, 1]:
        for y in [-1, 1]:
            bumpPts.append(gmsh.model.geo.addPoint(x, y, 0,  meshSize=0.05)) 

    bumpPts[2], bumpPts[3] = bumpPts[3], bumpPts[2]

    for x in [0, 1]:
        for y in [-1, 1]:
            bumpPts.append(gmsh.model.geo.addPoint(x, y, 0.2,  meshSize=0.05))

    bumpPts[6], bumpPts[7] = bumpPts[7], bumpPts[6]

    # build bump surface 
    bumpLine = []
    for i in range(4):
        bumpLine.append(gmsh.model.geo.addLine(bumpPts[i], bumpPts[(i+1)%4]))

    for i in range(4):
        bumpLine.append(gmsh.model.geo.addLine(bumpPts[i], bumpPts[i+4]))

    for i in range(4):
        bumpLine.append(gmsh.model.geo.addLine(bumpPts[i+4], bumpPts[(i+1)%4+4]))

    # build bump surface 
    bumpSurface = []

    temp = gmsh.model.geo.addCurveLoop([bumpLine[0], bumpLine[1], bumpLine[2], bumpLine[3]], reorient=True)
    bumpSurface.append(gmsh.model.geo.addPlaneSurface([temp]))

    for i in range(4):
        temp = gmsh.model.geo.addCurveLoop([bumpLine[i], bumpLine[(i+1)%4+4], bumpLine[i+8], bumpLine[i+4]], reorient=True)
        bumpSurface.append(gmsh.model.geo.addSurfaceFilling([temp]))

    temp = gmsh.model.geo.addCurveLoop([bumpLine[8], bumpLine[9], bumpLine[10], bumpLine[11]], reorient=True)
    bumpSurface.append(gmsh.model.geo.addPlaneSurface([temp]))

    # build plate points
    platePts = []
    for x in [-3, 2]:
        for y in [-2, 2]:
            platePts.append(gmsh.model.geo.addPoint(x, y, 0.00, meshSize=0.4))

    # swap order for convinience
    platePts[2], platePts[3] = platePts[3], platePts[2]

    # build plate line 
    plateLine = []
    for i in range(4):
        plateLine.append(gmsh.model.geo.addLine(platePts[i], platePts[(i+1)%4])) 

    for i in range(4):
        plateLine.append(gmsh.model.geo.addLine(platePts[i], bumpPts[i])) 

    # build plate surface
    for i in range(4):
        temp = [plateLine[i], plateLine[(i+1)%4+4], bumpLine[i], plateLine[i+4]]
        bumpSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop(temp, reorient=True)]))

    gmsh.model.geo.synchronize()
    gmsh.model.addPhysicalGroup(2, bumpSurface, name='bump')

    gmsh.option.setNumber("Mesh.Algorithm", 5)
    
    gmsh.model.mesh.generate(2)

    name = sys.argv[1]
    gmsh.write(f'{name}.stl')
    # gmsh.write(f'{name}.vtk')
    
    gmsh.finalize()


if __name__ == '__main__':
    # bumpTriGen(bumpMeshSize=0.02, plateMeshSize=0.2,k=0.5, c=0.1)
    fakeBumpGen()