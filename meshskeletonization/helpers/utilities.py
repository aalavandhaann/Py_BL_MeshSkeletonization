import bpy, bmesh, time, mathutils;
import numpy as np;
import scipy as sp;
import scipy.sparse as spsp;

from mathutils import Vector;

#Return object bounds as minvector and maxvector
def getObjectBounds(mesh):
    minx = miny = minz = 9999999999999999;
    maxx = maxy = maxz = -9999999999999999;    
    bounds = [Vector(b) for b in mesh.bound_box];

    xvalues = [b.x for b in bounds];
    yvalues = [b.y for b in bounds];
    zvalues = [b.z for b in bounds];
    
    minx = min(xvalues);
    maxx = max(xvalues);

    miny = min(yvalues);
    maxy = max(yvalues);

    minz = min(zvalues);
    maxz = max(zvalues);
    
    return Vector((min(xvalues), min(yvalues), min(zvalues))), Vector((max(xvalues), max(yvalues),  max(zvalues)));

def getBBox(m):
    min_coords, max_coords = getObjectBounds(m);
    dimensionvector = max_coords - min_coords;
    diameter = dimensionvector.length;
    return min_coords, max_coords, diameter;

def meanCurvatureLaplaceWeights(context, mesh, symmetric = False, normalized=False):
    start = time.time();
    
    bm = getBMMesh(context, mesh, useeditmode=False);
    ensurelookuptable(bm);
    
    rows = [];
    cols = [];
    data = [];
    n = len(mesh.data.vertices);
    for f in bm.faces:
        v1, v2, v3 = [l.vert for l in f.loops];
        v1v2 = v1.co - v2.co;
        v1v3 = v1.co - v3.co;
        
        v2v1 = v2.co - v1.co;
        v2v3 = v2.co - v3.co;
        
        v3v1 = v3.co - v1.co;
        v3v2 = v3.co - v2.co;            
        
        cot1 = v2v1.dot(v3v1) / max(v2v1.cross(v3v1).length,1e-06);
        cot2 = v3v2.dot(v1v2) / max(v3v2.cross(v1v2).length,1e-06);
        cot3 = v1v3.dot(v2v3) / max(v1v3.cross(v2v3).length,1e-06);
        
        rows.append(v2.index);
        cols.append(v3.index);
        data.append(cot1);
        
        rows.append(v3.index);
        cols.append(v2.index);
        data.append(cot1);
        
        rows.append(v3.index);
        cols.append(v1.index);
        data.append(cot2);
        
        rows.append(v1.index);
        cols.append(v3.index);
        data.append(cot2);
        
        rows.append(v1.index);
        cols.append(v2.index);
        data.append(cot3);
        
        rows.append(v2.index);
        cols.append(v1.index);
        data.append(cot3);           
    
    W = spsp.csr_matrix((data, (rows, cols)), shape = (n,n));
    
    if(symmetric and not normalized):
        sum_vector = W.sum(axis=0);
        d = spsp.dia_matrix((sum_vector, [0]), shape=(n,n));
        L = d - W;
    elif(symmetric and normalized):
        sum_vector = W.sum(axis=0);
        sum_vector_powered = np.power(sum_vector, -0.5);
        d = spsp.dia_matrix((sum_vector_powered, [0]), shape=(n,n));
        eye = spsp.identity(n);
        L = eye - d * W * d;
    elif (not symmetric and normalized):
        sum_vector = W.sum(axis=0);
        sum_vector_powered = np.power(sum_vector, -1.0);
        d = spsp.dia_matrix((sum_vector_powered, [0]), shape=(n,n));
        eye = spsp.identity(n);
        L = eye - d * W;
    else:
        L = W;
    
    bm.free();
       
    if(not context.mode == "OBJECT"):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False);
    
    end = time.time();
    print("FINISHED CONSTRUCTING WEIGHTS FOR ", mesh.name, " IN ", (end - start)); 
    return L;


def getDuplicatedObject(context, meshobject, meshname="Duplicated", wire = False):
        if(not context.mode == "OBJECT"):
            bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False);

        bpy.ops.object.select_all(action='DESELECT') #deselect all object
        
        hide_selection = meshobject.hide_select;
        hide_view = meshobject.hide;
        
        meshobject.hide_select = False;
        meshobject.hide = False;
        
        #The next step is to duplicate these objects and then apply fairing on them
        meshobject.select = True;
        context.scene.objects.active = meshobject;
        bpy.ops.object.duplicate_move();

        meshobject.select = False;

        duplicated = context.active_object;
        duplicated.location.x = 0;
        duplicated.location.y = 0;
        duplicated.location.z = 0;
        duplicated.name = meshname;
        duplicated.show_wire = wire;
        duplicated.show_all_edges = wire;
        duplicated.data.name = meshname;

        meshobject.hide_select = hide_selection;
        meshobject.hide = hide_view;

        return duplicated;

def getMeshVPos(mesh, extra_points=[]):
    vpos = [];
    for v in mesh.data.vertices:
        vpos.append([v.co.x, v.co.y, v.co.z]);
    
    for p in extra_points:
        vpos.append([p.x, p.y, p.z]);
    
    return np.array(vpos);

def getBMMesh(context, obj, useeditmode = True):
    if(not useeditmode):
        if(context.mode == "OBJECT"):
            bm = bmesh.new();
            bm.from_mesh(obj.data);
        else:
            bm = bmesh.from_edit_mesh(obj.data);
            
            if context.mode != 'EDIT_MESH':
                bpy.ops.object.mode_set(mode = 'EDIT', toggle = False);

        return bm;

    else:
        if(context.mode != "OBJECT"):
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False);

        bpy.ops.object.select_all(action='DESELECT') #deselect all object
        context.scene.objects.active = obj;
        obj.select = True;
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False);
        bm = bmesh.from_edit_mesh(obj.data);
        return bm;

def ensurelookuptable(bm):
    try:
        bm.verts.ensure_lookup_table();
        bm.edges.ensure_lookup_table();
        bm.faces.ensure_lookup_table();
    except:
        print('THIS IS AN OLD BLENDER VERSION, SO THIS CHECK NOT NEEDED');


def averageFaceArea(c, mesh):
    bm = getBMMesh(c, mesh, useeditmode=False);
    ensurelookuptable(bm);
    area = [];
    for f in bm.faces:
        v1, v2, v3 = [l.vert for l in f.loops];
        area.append(f.calc_area());
    bm.free();    
    return 1.0 / (10.0 * np.sqrt(np.mean(area)));

def getOneRingAreas(c, mesh):
    onebyeight = 1.0 / 8.0;
    oneringareas = [];
    bm = getBMMesh(c, mesh, useeditmode=False);
    ensurelookuptable(bm);
    
    for v in bm.verts:
        v_one_ring_area = [];
        for f in v.link_faces:
            v_one_ring_area.append(f.calc_area());
        
        oneringareas.append(np.min(np.sqrt(np.sum(np.square(v_one_ring_area)))));
        
    bm.free();    
    return np.array(oneringareas);



#Can be of kd_type, 1-VERT, 2-EDGE, 3-FACE, 4-FACEVERT (contains vertices co with face Index)
#5-EDGEVERT (contains vertices co with EDGE INDEX)
def buildKDTree(context, meshobject, kd_type="VERT", points=[], use_bm =None,*, return_points = False):
#     print('BUILDING KDTREE FOR ', object.name);
    if(meshobject):
        mesh = meshobject.data;
        data = [];    
    if(kd_type == "VERT"):
        size = len(mesh.vertices);
        kd = mathutils.kdtree.KDTree(size);
        for i, v in enumerate(mesh.vertices):
            kd.insert(v.co, v.index);
    elif(kd_type =="EDGE"):
        subdivisions = 3;
        subdivisionsF = 3.0;
        size = len(mesh.edges) * subdivisions;
        edge_points = [];
        kd = mathutils.kdtree.KDTree(size);
        
        for i, e in enumerate(mesh.edges):
            v0 = mesh.vertices[e.vertices[0]].co;
            v1 = mesh.vertices[e.vertices[1]].co;
            vect = (v1 - v0);
            
            for i in range(subdivisions):
                ratio = float(i) / (subdivisionsF - 1.0);
                point = v0 + (vect * ratio);
                kd.insert(point, e.index);
                edge_points.append({'index':e.index, 'co':point});
                
        if(return_points):
            kd.balance();
            return kd, edge_points;
        
        
    elif(kd_type =="FACE"):
        size = len(mesh.polygons);
        kd = mathutils.kdtree.KDTree(size);
        oneby3 = 1.0 / 3.0;
        loops = meshobject.data.loops;
        vertices = meshobject.data.vertices;
        
        for i, f in enumerate(mesh.polygons):
                        
#             v0 = vertices[loops[f.loop_indices[0]].vertex_index].co;
#             v1 = vertices[loops[f.loop_indices[1]].vertex_index].co;
#             v2 = vertices[loops[f.loop_indices[2]].vertex_index].co;
            
#             point = (v0 * oneby3) + (v1 * oneby3) + (v2 * oneby3);
            kd.insert(f.center.copy(), f.index);
#             point, mat = getCentroid([v0, v1, v2]);
#             kd.insert(mat * point, f.index);
    
    elif(kd_type == "FACEVERT"):
        size = len(mesh.polygons) * 3;
        kd = mathutils.kdtree.KDTree(size);

        for i, f in enumerate(mesh.polygons):
            if(len(f.loop_indices) > 3):
                print('GOTCHA :: THE BLACK SHEEP ::: ', object.name, f.index);
            for ind in f.loop_indices:
                l = mesh.loops[ind];
                v = mesh.vertices[l.vertex_index];
                kd.insert(v.co, f.index);            
    
    elif(kd_type == "CUSTOM"):
        size = len(points);
        kd = mathutils.kdtree.KDTree(size);
        useDict = True;
        try:
            index = points[0]['index'];
        except KeyError:            
            useDict = False;
        except TypeError:
            useDict = False;
        except IndexError:
            useDict = False;
        
        for i, point in enumerate(points):
            if(useDict):
                index = point['index'];
                co = point['co'];
                kd.insert(co, index);
            else:
                kd.insert(point, i);          
                
    kd.balance();
#     print('BUILD KD TREE OF SIZE : ', size, ' FOR :: ', object.name, ' USING TYPE : ', kd_type);
    return kd;



