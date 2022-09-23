
def bumpBuild(k : float, c : float, meshControl : list = [0.01, 0.5, 1], xGrid : int = 21, yGrid : int = 41):
    import numpy as np
    delta = np.pi/28
    index = 0
    bumpMeshSize, plateMeshSize, globalMeshSize = meshControl 

    with open('bump.geo', 'w') as of:

        # Bump point define
        for x in np.linspace(0, 1.0, xGrid)*np.pi:
            temp_x = x**2*np.tan(delta)**2 + c
            for y in np.linspace(-1.0, 1.0, yGrid)*np.pi:
                temp = temp_x/(1/np.cos(np.arctan(y/k)))**2
                z = np.sqrt(temp) * np.sin(x) * np.sin((y+np.pi)/2)
                of.write(f'Point({index:d}) = {{{x/np.pi:.3f}, {y/np.pi:.3f}, {z:.6f}, {bumpMeshSize:f}}};\n')
                index += 1
        of.write('\n')

        # Plate point andl line define
        of.write('// plate points\n')
        of.write(f'Point(10001) = {{-5.00, -3.00, 0.00, {plateMeshSize:f}}};\n')
        of.write(f'Point(10002) = {{-5.00, 3.00, 0.00, {plateMeshSize:f}}};\n')
        of.write(f'Point(10003) = {{1.00, -3.00, 0.00, {plateMeshSize:f}}};\n')
        of.write(f'Point(10004) = {{1.00, 3.00, 0.00, {plateMeshSize:f}}};\n\n')
        
        of.write( 'Line(10001) = {0, 10001};\n')
        of.write( 'Line(10002) = {10001, 10002};\n')
        of.write(f'Line(10003) = {{10002, {yGrid-1:d}}};\n')
        of.write( 'Line(10004) = {10002, 10004};\n')
        of.write(f'Line(10005) = {{10004, {xGrid*yGrid-1:d}}};\n')
        of.write(f'Line(10006) = {{{(xGrid-1)*yGrid:d}, 10003}};\n')
        of.write( 'Line(10007) = {10003, 10001};\n\n')

        # Bottom point andl line define
        of.write('// bottom symetric\n')
        of.write(f'Point(20001) = {{-15, -10, 0, {globalMeshSize:f}}};\n')
        of.write(f'Point(20002) = {{-15, 10, 0, {globalMeshSize:f}}};\n')
        of.write(f'Point(20003) = {{10, -10, 0, {globalMeshSize:f}}};\n')
        of.write(f'Point(20004) = {{10, 10, 0, {globalMeshSize:f}}};\n\n')

        of.write( 'Line(20001) = {10001, 20001};\n')
        of.write( 'Line(20002) = {20001, 20002};\n')
        of.write( 'Line(20003) = {20002, 10002};\n')
        of.write( 'Line(20004) = {20002, 20004};\n')
        of.write( 'Line(20005) = {20004, 10004};\n')
        of.write( 'Line(20006) = {20004, 20003};\n')
        of.write( 'Line(20007) = {20003, 10003};\n')
        of.write( 'Line(20008) = {20003, 20001};\n\n')

        # Top point andl line define
        of.write('// top surface\n')
        of.write(f'Point(30001) = {{-15, -10, 10, {globalMeshSize:f}}};\n')
        of.write(f'Point(30002) = {{-15, 10, 10, {globalMeshSize:f}}};\n')
        of.write(f'Point(30003) = {{10, -10, 10, {globalMeshSize:f}}};\n')
        of.write(f'Point(30004) = {{10, 10, 10, {globalMeshSize:f}}};\n\n')
        
        of.write( 'Line(30001) = {30002, 30001};\n')
        of.write( 'Line(30002) = {30001, 30003};\n')
        of.write( 'Line(30003) = {30003, 30004};\n')
        of.write( 'Line(30004) = {30004, 30002};\n\n')

        # Inlet line define
        of.write('// inlet surface\n')
        of.write( 'Line(30005) = {30001, 20001};\n')
        of.write( 'Line(30006) = {30002, 20002};\n\n')

        # Outlet line define
        of.write('// outlet surface\n')
        of.write( 'Line(30007) = {30003, 20003};\n')
        of.write( 'Line(30008) = {30004, 20004};\n\n')

        # Y-dir bump line define
        of.write('// Y-direction main curve\n')
        of.write(f'Line(1) = {{0,{yGrid-1:d}}};\n')
        for i in range(2, xGrid):
            of.write(f'Spline({i:d}) = {{{yGrid*(i-1):d}:{yGrid*i-1:d}}};\n')
        of.write(f'Line({xGrid:d}) = {{{yGrid*(xGrid-1):d},{yGrid*xGrid-1:d}}};\n\n')

        # X-dir bump line define
        of.write('// X-direction edge curve (negative Y side)\n')
        for i in range(xGrid-1):
            of.write(f'Line({xGrid+1+i:d}) = {{{yGrid*i:d},{yGrid*(i+1):d}}};\n')
        of.write('\n')

        of.write('// X-direction edge curve (positive Y side)\n')
        for i in range(1,xGrid):
            of.write(f'Line({xGrid*2-1+i:d}) = {{{yGrid*i-1:d},{yGrid*(i+1)-1:d}}};\n')
        of.write('\n')

        # Bump surface define
        of.write('// bump surface\n')
        for i in range(1, xGrid):
            of.write(f'Line Loop({i}) = {{{i:d}, {xGrid*2-1+i:d}, {-(i+1):d}, {-(xGrid+i):d}}};\n')
            of.write(f'Surface({i:d}) = {{{i:d}}};\n')
        of.write('\n')

        # Plate surface define
        of.write('// plate surface\n')
        of.write( 'Line Loop(10001) = {10001, 10002, 10003, -1};\n')
        of.write( 'Plane Surface(10001) = {10001};\n')
        of.write(f'Line Loop(10002) = {{-10003, 10004, 10005, {-2*xGrid:d}:{-3*xGrid+2:d}}};\n')
        of.write( 'Plane Surface(10002) = {10002};\n')
        of.write(f'Line Loop(10003) = {{{xGrid+1:d}:{xGrid*2-1:d}, 10006, 10007, -10001}};\n')
        of.write( 'Plane Surface(10003) = {10003};\n\n')

        # Bottom surface define
        of.write('// bottom surface\n')
        of.write( 'Line Loop(20001) = {20001, 20002, 20003, -10002};\n')
        of.write( 'Plane Surface(20001) = {20001};\n')
        of.write( 'Line Loop(20002) = {-20003, 20004, 20005, -10004};\n')
        of.write( 'Plane Surface(20002) = {20002};\n')
        of.write(f'Line Loop(20003) = {{-20005, 20006, 20007, -10006, {xGrid:d}, -10005}};\n')
        of.write( 'Plane Surface(20003) = {20003};\n')
        of.write( 'Line Loop(20004) = {20008, -20001, -10007, -20007};\n')
        of.write( 'Plane Surface(20004) = {20004};\n\n')

        # Others surface define
        of.write('// top surface\n')
        of.write( 'Line Loop(30001) = {30001, 30002, 30003, 30004};\n')
        of.write( 'Plane Surface(30001) = {30001};\n\n')

        of.write( '// inlet surface\n')
        of.write( 'Line Loop(30002) = {30006, -20002, -30005, -30001};\n')
        of.write( 'Plane Surface(30002) = {30002};\n\n')

        of.write( '// right surface\n')
        of.write( 'Line Loop(30003) = {30008, -20004, -30006, -30004};\n')
        of.write( 'Plane Surface(30003) = {30003};\n\n')

        of.write( '// outlet surface \n')
        of.write( 'Line Loop(30004) = {30007, -20006, -30008, -30003};\n')
        of.write( 'Plane Surface(30004) = {30004};\n\n')

        of.write( '// left surface \n')
        of.write( 'Line Loop(30005) = {30005, -20008, -30007, -30002};\n')
        of.write( 'Surface(30005) = {30005};\n\n')

        # Volume define
        of.write( '// volume\n')
        of.write(f'Surface Loop(1) = {{20001, 20002, 10001, 10002, 1:{xGrid-1:d}, 10003, 20003, 20004, 30002:30005, 30001}};\n')
        of.write( 'Volume(1) = {1};\n\n')

        of.write(f'Physical Surface("bump") = {{1:{xGrid-1:d}}};\n')
        of.write( 'Physical Surface("plate") = {10001:10003};\n')
        of.write( 'Physical Surface("bottom") = {20001:20004};\n')
        of.write( 'Physical Surface("top") = {30001};\n')
        of.write( 'Physical Surface("inlet") = {30002};\n')
        of.write( 'Physical Surface("right") = {30003};\n')
        of.write( 'Physical Surface("outlet") = {30004};\n')
        of.write( 'Physical Surface("left") = {30005};\n')
        of.write( 'Physical Volume("internal") = {1};\n')


if __name__ == '__main__':
    bumpBuild(k=1.3, c=0.0, meshControl=[0.005, 0.2, 1], xGrid=21, yGrid=41)