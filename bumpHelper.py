import numpy as np


def bumpBuild(k : float, c : float, xGrid : int = 21, yGrid : int = 42):
    

# k, c = 1.3, 0.0
# delta = np.pi/28
# index = 0


# with open('bump.txt', 'w') as of:
#     for x in np.linspace(0, 1.0, 11)*np.pi:
#         temp_x = x**2*np.tan(delta)**2 + c
#         for y in np.linspace(-1.0, 1.0, 21)*np.pi:
#             temp = temp_x/(1/np.cos(np.arctan(y/k)))**2
#             z = np.sqrt(temp) * np.sin(x) * np.sin((y+np.pi)/2)
#             of.write(f'Point({index:d}) = {{{x/np.pi:.3f}, {y/np.pi:.3f}, {z:.5f}, 0.005}};\n')
#             index += 1