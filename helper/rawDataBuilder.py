"""

name : rawDataBuilder.py
usage : Build raw data in following steps : 
        1. Link mesh file to case root folder
        2. Modified boundary condition (Mach number)
        3. Run simulation
        4. Create total pressure field 
        5. Move data file to target folder
author : Bo-Yuan You
Date : 2023-01-11

"""

import numpy as np
import os, sys

class RDB():
    """
    rawDataBuilder (RDB)

    Generator class build cfd raw data for given geometry parameters set and flow condition
    """
    def __init__(self, geoName) -> None:
        pass
