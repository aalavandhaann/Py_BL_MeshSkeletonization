import bpy, time;
import numpy as np;
import scipy as sp;

from meshskeletonization.helpers.utilities import getBMMesh, ensurelookuptable;
from meshskeletonization.helpers.utilities import meanCurvatureLaplaceWeights;

from meshskeletonization.helpers.utilities import averageFaceArea, getOneRingAreas;
from meshskeletonization.helpers.meshcontraction import meshContraction;

def skeletonize(c, m, iterations=10):
    dm = meshContraction(c, m, iterations);
    return dm;

