import gmsh, sys
import numpy as np

def bumpTriGen(bumpMeshSize : float = 0.01, k : float = 1.3, c : float = 0.1, xGrid : int = 51, yGrid : int = 101, scaleFactor : float = 1.0) -> None:

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

        gmsh.model.geo.synchronize()
        gmsh.model.addPhysicalGroup(2, bumpSurface, name='bump')
        # gmsh.model.addPhysicalGroup(2, [bumpBottomSurface], name='bottom')

        gmsh.option.setNumber("Mesh.Algorithm", 6)
        
        gmsh.model.mesh.generate(2)

        gmsh.write('bump.stl')
        gmsh.write('bump.vtk')
        
        gmsh.finalize()

if __name__ == '__main__':
    bumpTriGen(k=0.5, c=0.0)