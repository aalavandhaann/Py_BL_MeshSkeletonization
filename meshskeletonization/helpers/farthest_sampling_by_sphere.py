import numpy as np;
from meshskeletonization.helpers.utilities import buildKDTree, getMeshVPos

def farthest_sampling_by_sphere(context, mesh, radius):
    n = len(mesh.data.vertices);
    kdtree = buildKDTree(context, mesh);
    spls = np.zeros((0, 3));
    corresp = np.zeros((n, 1));
    mindst = np.zeros((n, 1));
    mindst[:] = np.nan;
    pts = getMeshVPos(mesh);
    for k in range(n):
        vco = mesh.data.vertices[k];
        
        if(corresp[k] != 0.0):
            continue;
        
        mindst[k] = np.inf;
        
        while (not np.all(corresp != 0.0)):
            maxIdx = np.argmax(mindst);
            maxValue = mindst[maxIdx];
            
            if(mindst[maxIdx] == 0.0):
                break;
            
            valuesInRange = kdtree.find_range(vco, radius);
            if(len(valuesInRange)):
                valuesInRange = np.array(valuesInRange);
                nIdxs, nDsts = valuesInRange[:,1], valuesInRange[:,2];
                if(np.all(corresp[nIdxs] !=0.0)):
                    mindst[maxIdx] = 0.0;
                    continue;
            
            
                spls = np.append(spls, [pts[maxIdx,:]]);
                for i in range(nIdxs):
                    if(mindst[nIdxs[i]] > nDsts[i] or np.isnan(mindst[nIdxs[i]])):
                        mindst[nIdxs[i]] = nDsts[i];
                        corresp[nIdxs[i]] = spls.shape[0];
    
    
    return spls, corresp;
    
    
    
    
                    
            