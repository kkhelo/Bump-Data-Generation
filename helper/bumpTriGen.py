import gmsh, sys, os
import numpy as np

def bumpTriGen(bumpMeshSize : float = 0.01, plateMeshSize : float = 0.05, domainMeshSize : float = 0.5, k : float = 1.3, c : float = 0.1, d: int = 28, xGrid : int = 41, yGrid : int = 81, scaleFactor : float = 0.5) -> None:

        gmsh.initialize(sys.argv)
        gmsh.model.add('bump')

        gmsh.option.setNumber('General.NumThreads', 20)
        gmsh.option.setNumber('General.Terminal', 1)
        gmsh.option.setNumber('General.ExpertMode', 1)
        gmsh.option.setNumber('Mesh.MshFileVersion', 2)

        delta = np.pi/d
        pts, index = [], 0
        for x in np.linspace(0, 1.0, xGrid)*np.pi:
            temp_x = x**2*np.tan(delta)**2 + c
            for y in np.linspace(-1.0, 1.0, yGrid)*np.pi:
                rSquare = temp_x/(1/np.cos(np.arctan(y/k)))**2
                z = np.sqrt(rSquare) * np.sin(x) * np.sin((y+np.pi)/2)
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
            x *= scaleFactor
            for y in [-2, 2]:
                
                y *= scaleFactor
                print(x, y)
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
        for x in [-10, 15]:
            x *= scaleFactor
            for y in [-10, 10]:
                y *= scaleFactor 
                domainPtsBottom.append(gmsh.model.geo.addPoint(x, y, 0, meshSize=domainMeshSize))
                domainPtsUpper.append(gmsh.model.geo.addPoint(x, y, 10*scaleFactor, meshSize=domainMeshSize))

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
        domainSurface.append(gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([-domainLineTop[i] for i in range(3,-1,-1)])]))

        gmsh.model.geo.synchronize()

        gmsh.model.addPhysicalGroup(2, domainSurface[0], name='bottom')
        gmsh.model.addPhysicalGroup(2, [domainSurface[1]], name='inlet')
        gmsh.model.addPhysicalGroup(2, [domainSurface[2]], name='right')
        gmsh.model.addPhysicalGroup(2, [domainSurface[3]], name='outlet')
        gmsh.model.addPhysicalGroup(2, [domainSurface[4]], name='left')
        gmsh.model.addPhysicalGroup(2, [domainSurface[5]], name='top')
        gmsh.model.addPhysicalGroup(2, plateSurface, name='plate')
        gmsh.model.addPhysicalGroup(2, bumpSurface, name='bump')

        gmsh.option.setNumber("Mesh.Algorithm", 5)
        
        gmsh.model.mesh.generate(2)

        name = f'k{int(k*100):d}_c{int(c*100):d}_d{d:d}.stl'
        
        # # training geometry
        # if not os.path.exists('./stlBump') : os.mkdir('./stlBump')
        # gmsh.write(os.path.join('./stlBump', name))

        # testing geometry
        if not os.path.exists('./stlBumpTest') : os.mkdir('./stlBumpTest')
        gmsh.write(os.path.join('./stlBumpTest', name))

        # gmsh.write('test.geo_unrolled')
        
        gmsh.finalize()

if __name__ == '__main__':

    # # training geometry
    # for k in [0.5, 0.75, 1.0]:
    #     for c in [0.1, 0.3, 0.5]:
    #         for d in [28, 21, 14]:
    #             bumpTriGen(bumpMeshSize=0.01, plateMeshSize=0.2,k=k, c=c, d=d, xGrid = 101, yGrid=201)

    # # testing geometry
    # for k in [0.8, 1.3]:  
    #     for c in [0.2, 0.6]:
    #         for d in [20, 30]:
    #             bumpTriGen(bumpMeshSize=0.01, plateMeshSize=0.2,k=k, c=c, d=d, xGrid = 101, yGrid=201)

    # testing geometry2
    for k in [0.6, 0.8]:  
        for c in [0.2, 0.4]:
            for d in [20, 30]:
                bumpTriGen(bumpMeshSize=0.01, plateMeshSize=0.2,k=k, c=c, d=d, xGrid = 101, yGrid=201)

    # bumpTriGen(bumpMeshSize=0.01, plateMeshSize=0.2,k=0.5, c=0.5, d=28, xGrid = 41, yGrid=81)