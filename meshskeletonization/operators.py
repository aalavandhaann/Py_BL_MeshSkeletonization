import bpy;
from meshskeletonization.helpers.meshcontraction import meshContraction
from meshskeletonization.helpers.utilities import getBBox
from meshskeletonization.helpers.farthest_sampling_by_sphere import farthest_sampling_by_sphere

#The operator for doing the Joint Fairing step
class MeshContractionByLaplacian(bpy.types.Operator):
    bl_idname = "ashok.meshcontractionbylaplacian";
    bl_label = "Mesh Contraction";
    bl_description = "Operator to do the mesh contraction using mean curvature laplacian"
    bl_space_type = "VIEW_3D";
    bl_region_type = "UI";
    bl_context = "objectmode";
    currentobject = bpy.props.StringProperty(name='currentobject', default="---");
    
    def execute(self, context):
        try:            
            mesh = bpy.data.objects[self.currentobject];
        except:
            mesh = context.active_object;
        
        if(mesh is not None):
            dmesh = meshContraction(context, mesh, iterations=mesh.iterations, SL=mesh.sl, WC=mesh.wc);
            mesh.select = True;
            context.scene.objects.active = mesh;
            mesh.contractedmesh = dmesh.name;
            self.report({'INFO'}, "Mesh contraction finished successfully");
            return {'FINISHED'};
        else:
            self.report({'ERROR'}, "No Mesh is selected");
        
        return {'FINISHED'};
    

#The operator for doing the Joint Fairing step
class LineExtraction(bpy.types.Operator):
    bl_idname = "ashok.lineextration";
    bl_label = "Line Extraction";
    bl_description = "Extract the 1D line from laplacian contracted mesh"
    bl_space_type = "VIEW_3D";
    bl_region_type = "UI";
    bl_context = "objectmode";
    currentobject = bpy.props.StringProperty(name='currentobject', default="---");
    
    def execute(self, context):
        mesh, dmesh = None, None;
        try:            
            mesh = bpy.data.objects[self.currentobject];
        except:
            mesh = context.active_object;
        
        if(mesh is not None):
            try:
                dmesh = context.scene.objects[mesh.contractedmesh];
            except:
                bpy.ops.ashok.meshcontractionbylaplacian('EXEC_DEFAULT', currentobject=mesh.name);
                dmesh = context.scene.objects[mesh.contractedmesh];
        
        if(dmesh is not None):
            min_coords, max_coords, diameter = getBBox(mesh);
            sample_radius = diameter*0.02;
            spls, corresp = farthest_sampling_by_sphere(context, dmesh, sample_radius);
            print(spls.shape);
            print(corresp.shape);
            self.report({'INFO'}, "Mesh contraction finished successfully");
            return {'FINISHED'};
        else:
            self.report({'ERROR'}, "No Mesh is selected");
        
        return {'FINISHED'};




def register():
    bpy.utils.register_class(MeshContractionByLaplacian);
    bpy.utils.register_class(LineExtraction);

def unregister():
    bpy.utils.unregister_class(MeshContractionByLaplacian);
    bpy.utils.unregister_class(LineExtraction);