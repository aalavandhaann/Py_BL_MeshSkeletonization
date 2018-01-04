import bpy;
import time;
import numpy as np;
import scipy as sp;
from scipy.sparse.linalg import lsqr, lsmr;

from meshskeletonization.helpers.utilities import meanCurvatureLaplaceWeights;
from meshskeletonization.helpers.utilities import getDuplicatedObject, getMeshVPos;

from meshskeletonization.helpers.utilities import averageFaceArea, getOneRingAreas;

#Given a mesh, create a duplicate and return the contracted representation of the given mesh
# c - context (bpy.context);
# m - The mesh to be applied with contraction
# iterations - total number of iterations to apply with
# SL - initial faceweights are multiplied with this weights for each iteration
# WC - initial weighting factor to start with

def meshContraction(c, m, iterations=10, SL=10.0, WC=10.0):
    n = len(m.data.vertices);
    initialFaceWeight = averageFaceArea(c, m);
    originalOneRing = getOneRingAreas(c, m);
    zeros = np.zeros((n,3));
    
    full_start = time.time();
    np_WL0 = np.zeros((n,n));
    np.fill_diagonal(np_WL0, initialFaceWeight);
    WH0 = sp.sparse.dia_matrix(np.eye(n) * WC);
    WL0 = sp.sparse.dia_matrix(np_WL0);
    
    try:
        dm = c.scene.objects[m.name+"_skel_It"+str(iterations)+"_SL"+str(SL)+"_WC"+str(WC)];
    except KeyError:
        dm = getDuplicatedObject(c, m, m.name+"_skel_It"+str(iterations)+"_SL"+str(SL)+"_WC"+str(WC));
    
    bpy.ops.object.select_all(action="DESELECT");
    dm.select = True;
    c.scene.objects.active = dm;
    
    L = -meanCurvatureLaplaceWeights(c, dm, normalized=True);
    WL = sp.sparse.dia_matrix(WL0);
    WH = sp.sparse.dia_matrix(WH0);

    area_ratios = [];
    area_ratios.append(1.0);
    originalFaceAreaSum = np.sum(originalOneRing);
    goodvertices = [[]];
    timetracker = [];    
    
    for i in range(iterations):
        print('*' * 40);
        print('ITERATION : %d'%i);
        start = time.time();
        vpos = getMeshVPos(dm);
        A = sp.sparse.vstack([L.dot(WL), WH]);
        b = np.vstack((zeros, WH.dot(vpos)));
        cpts = np.zeros((n,3));
        
        for j in range(3):
            cpts[:, j] = lsqr(A, b[:, j])[0];

        for v in dm.data.vertices:
            v.co = tuple(cpts[v.index]);
            
        end = time.time();
        print('TOTAL TIME FOR SOLVING LEAST SQUARES ::: ' , (end - start));
        newringareas = getOneRingAreas(c, dm);
        changeinarea = np.power(newringareas, -0.5);
        area_ratios.append(np.sum(newringareas) / originalFaceAreaSum);
        
        if(area_ratios[-1] > area_ratios[-2]):
            print('FACE AREA INCREASED FROM PREVIOUS ::: ', area_ratios[-1], area_ratios[-2]);
            print('ITERATION TERMINATED AT :::: ', i);
            print('RESTORE TO PREVIOUS GOOD POSITIONS FROM ITERATION ', i - 1);
            
            cpts = goodvertices[0];
            for v in dm.data.vertices:
                v.co = tuple(cpts[v.index]);
            break;    
        
        goodvertices[0] = cpts;
        print('RATIO OF CHANGE IN FACE AREA ::: ' , area_ratios[-1]);    
        WL = sp.sparse.dia_matrix(WL.multiply(SL));
        WH = sp.sparse.dia_matrix(WH0.multiply(changeinarea));
        L = -meanCurvatureLaplaceWeights(c, dm, normalized=True);
        full_end = time.time();
        
        timetracker.append(full_end - full_start);
        full_start = time.time();
    
    print('TOTAL TIME FOR MESH CONTRACTION ::: ', np.sum(timetracker), ' FOR VERTEX COUNT ::: #',n);    
    return dm;
