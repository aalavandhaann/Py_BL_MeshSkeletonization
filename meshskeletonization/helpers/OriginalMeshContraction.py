import bpy, time;
import numpy as np;
import scipy as sp;
from scipy.sparse.linalg import lsqr, lsmr;
from sfmsuite.basics.mathtoolbox import getWeightsMatrix, getVoronoiArray, getTriangleArea;
from sfmsuite.basics.MeshToolBox import getBMMesh, ensurelookuptable, getMeshVPos, getDuplicatedObject;
from sfmsuite.basics.MeshOperators import meanCurvatureLaplaceWeights;

def averageFaceArea(c, mesh):
    bm = getBMMesh(c, mesh, useeditmode=False);
    ensurelookuptable(bm);
    area = [];
    for f in bm.faces:
        v1, v2, v3 = [l.vert for l in f.loops];
#        a, b, c = np.array(v1.co.to_tuple()), np.array(v2.co.to_tuple()), np.array(v3.co.to_tuple());
#        a = 0.5 * np.linalg.norm(np.cross(a - c, b - c));
#        area.append(a);
        area.append(f.calc_area());
    bm.free();    
    return 1.0 / (10.0 * np.sqrt(np.mean(area)));

def getOneRingAreas(c, mesh):
    
#    mesh.vertexvoronoi.clear();
#    bpy.ops.ashok.voronoioperator('EXEC_DEFAULT', currentobject=mesh.name);
#    return getVoronoiArray(mesh);

    onebyeight = 1.0 / 8.0;
    oneringareas = [];
    bm = getBMMesh(c, mesh, useeditmode=False);
    ensurelookuptable(bm);
    
    for v in bm.verts:
        v_one_ring_area = [];
        for f in v.link_faces:
            v_one_ring_area.append(f.calc_area());
        
        oneringareas.append(np.min(np.sqrt(np.sum(np.square(v_one_ring_area)))));
#        oneringareas.append(onebyeight * np.sum(v_one_ring_area**2));
        
    bm.free();    
    return np.array(oneringareas);


c = bpy.context;
m = c.active_object;
iterations = 10;
n = len(m.data.vertices);
SL = 10.0;
initialFaceWeight = averageFaceArea(c, m);
originalOneRing = getOneRingAreas(c, m);
ovpos = getMeshVPos(m);
zeros = np.zeros((n,3));

np_WL0 = np.zeros((n,n));
np.fill_diagonal(np_WL0, initialFaceWeight);
WC = 10.0;
WH0 = sp.sparse.dia_matrix(np.eye(n) * WC);
WL0 = sp.sparse.dia_matrix(np_WL0);

try:
    dm = c.scene.objects[m.name+"_skeleton_"+str(iterations)];
except KeyError:
    dm = getDuplicatedObject(c, m, m.name+"_skeleton_"+str(iterations));

bpy.ops.object.select_all(action="DESELECT");
dm.select = True;
c.scene.objects.active = dm;

dm.vertexweights.clear();
#dm.weighttype = 'Cotangents';
#bpy.ops.ashok.meshskeletonweightsoperator('EXEC_DEFAULT', currentobject=dm.name);
L = -meanCurvatureLaplaceWeights(c, dm, normalized=True);#getWeightsMatrix(dm, normalized=True);
WL = sp.sparse.dia_matrix(WL0);
WH = sp.sparse.dia_matrix(WH0);
TC = 0.01;

area_ratios = [];
area_ratios.append(1.0);
originalFaceAreaSum = np.sum(originalOneRing);
goodvertices = [[]];
timetracker = [];
for i in range(iterations):
    full_start = time.time();
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
#    changeinarea = np.sqrt(originalOneRing / newringareas);
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
#    WH = sp.sparse.dia_matrix(WH0.multiply(changeinarea));
    WH = sp.sparse.dia_matrix(WH0.multiply(changeinarea));
#    dm.vertexweights.clear();
#    dm.weighttype = 'Cotangents';
#    bpy.ops.ashok.meshskeletonweightsoperator('EXEC_DEFAULT', currentobject=dm.name);
    L = -meanCurvatureLaplaceWeights(c, dm, normalized=True);
    full_end = time.time();
    
    timetracker.append(full_end - full_start);
    
print('TOTAL TIME FOR MESH CONTRACTION ::: ', np.sum(timetracker), ' FOR VERTEX COUNT ::: #',n);